/* eslint-disable no-console */
const fs = require("fs");
const path = require("path");
const { chromium } = require("@playwright/test");
const { parse } = require("csv-parse/sync");
const dotenv = require("dotenv");

dotenv.config();

const ALLOWED_FIELDS = new Set([
  "living_wage_link_national",
  "minimum_wage_link_english",
  "minimum_wage_link_national",
]);

function parseArgs(argv) {
  const args = {
    csv: null,
    assignee: process.env.OSHUB_ASSIGNEE_EMAIL || "",
    dryRun: false,
    includeDone: false,
    checkCsv: false,
    headless: process.env.HEADLESS !== "false",
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--csv") {
      args.csv = argv[i + 1];
      i += 1;
    } else if (arg === "--assignee") {
      args.assignee = argv[i + 1];
      i += 1;
    } else if (arg === "--dry-run") {
      args.dryRun = true;
    } else if (arg === "--include-done") {
      args.includeDone = true;
    } else if (arg === "--check-csv") {
      args.checkCsv = true;
    } else if (arg === "--headed") {
      args.headless = false;
    }
  }

  if (!args.csv) {
    throw new Error("Missing required argument: --csv <path>");
  }
  if (!args.assignee) {
    throw new Error(
      "Set OSHUB_ASSIGNEE_EMAIL in .env or pass --assignee <email>."
    );
  }

  return args;
}

function normalizeHeader(header) {
  return String(header || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
}

function getValue(row, aliases) {
  for (const key of aliases) {
    if (row[key] !== undefined) {
      return String(row[key] || "").trim();
    }
  }
  return "";
}

function loadChanges(csvPath, assigneeFilter, includeDone) {
  const raw = fs.readFileSync(csvPath, "utf8");
  const records = parse(raw, {
    columns: (headers) => headers.map(normalizeHeader),
    skip_empty_lines: true,
    trim: true,
  });

  const normalizedRows = records
    .map((row) => {
      const countryCode = getValue(row, ["country_code"]).toUpperCase();
      const fieldName = getValue(row, ["field_name"]);
      const oldLink = getValue(row, ["old_links", "old_link"]);
      const newLink = getValue(row, ["new_links", "new_link"]);
      const changeOwner = getValue(row, ["change_owner", "assignee"]);
      const status = getValue(row, ["status"]).toLowerCase();

      return {
        countryCode,
        fieldName,
        oldLink,
        newLink,
        changeOwner,
        status,
      };
    });

  const filteredByAssignee = normalizedRows.filter(
    (row) => row.changeOwner.toLowerCase() === assigneeFilter.toLowerCase()
  );

  const filteredByStatus = filteredByAssignee.filter(
    (row) => includeDone || row.status !== "done"
  );

  const changes = filteredByStatus.filter(
    (row) => row.countryCode && row.fieldName && row.newLink
  );

  const invalidFields = changes.filter((c) => !ALLOWED_FIELDS.has(c.fieldName));
  if (invalidFields.length > 0) {
    const fieldList = [...new Set(invalidFields.map((c) => c.fieldName))].join(", ");
    throw new Error(`Unsupported field_name in CSV: ${fieldList}`);
  }

  return {
    changes,
    stats: {
      totalRows: records.length,
      matchedAssignee: filteredByAssignee.length,
      matchedStatus: filteredByStatus.length,
      actionable: changes.length,
    },
  };
}

async function fillFirst(page, selectors, value) {
  for (const selector of selectors) {
    const element = page.locator(selector).first();
    if ((await element.count()) > 0) {
      await element.fill(value);
      return true;
    }
  }
  return false;
}

async function clickFirst(page, selectors) {
  for (const selector of selectors) {
    const element = page.locator(selector).first();
    if ((await element.count()) > 0) {
      await element.click();
      return true;
    }
  }
  return false;
}

async function login(page, baseUrl, email, password) {
  await page.goto(`${baseUrl}/admin/login/?next=/admin/api/wageindicatorcountrydata/`, {
    waitUntil: "domcontentloaded",
  });

  const emailFilled = await fillFirst(page, [
    "input[name='username']",
    "input[name='email']",
    "input#id_username",
    "input[type='email']",
  ], email);
  if (!emailFilled) {
    throw new Error("Could not find email/username input on login page.");
  }

  const pwdFilled = await fillFirst(page, [
    "input[name='password']",
    "input#id_password",
    "input[type='password']",
  ], password);
  if (!pwdFilled) {
    throw new Error("Could not find password input on login page.");
  }

  const clicked = await clickFirst(page, [
    "button[type='submit']",
    "input[type='submit']",
    ".submit-row input",
  ]);
  if (!clicked) {
    throw new Error("Could not find submit button on login page.");
  }

  await page.waitForLoadState("domcontentloaded");

  if (page.url().includes("/admin/login")) {
    throw new Error("Login failed or additional auth step required.");
  }
}

async function openCountryForm(page, baseUrl, countryCode) {
  await page.goto(
    `${baseUrl}/admin/api/wageindicatorcountrydata/?q=${encodeURIComponent(countryCode)}`,
    { waitUntil: "domcontentloaded" }
  );

  const rowLink = page.locator("#result_list tbody tr th.field-country_code a").first();
  if ((await rowLink.count()) === 0) {
    return false;
  }

  await rowLink.click();
  await page.waitForLoadState("domcontentloaded");
  return true;
}

async function updateOne(page, baseUrl, change, dryRun) {
  const found = await openCountryForm(page, baseUrl, change.countryCode);
  if (!found) {
    return { status: "not_found", details: "Country row not found in admin search." };
  }

  const field = page.locator(`input[name='${change.fieldName}']`).first();
  if ((await field.count()) === 0) {
    return { status: "field_missing", details: `Input field '${change.fieldName}' not found.` };
  }

  const currentValue = ((await field.inputValue()) || "").trim();

  if (change.oldLink && currentValue !== change.oldLink) {
    return {
      status: "old_link_mismatch",
      details: `Current value differs from expected old_link. Current: ${currentValue}`,
    };
  }

  if (currentValue === change.newLink) {
    return { status: "unchanged", details: "Already set to new_link." };
  }

  if (dryRun) {
    return { status: "dry_run", details: `Would update '${change.fieldName}'.` };
  }

  await field.fill(change.newLink);
  const saveClicked = await clickFirst(page, [
    "input[name='_save']",
    "button[name='_save']",
    ".submit-row input.default",
  ]);
  if (!saveClicked) {
    return { status: "save_failed", details: "Save button not found." };
  }

  const successMessage = page.locator(".messagelist .success").first();
  if ((await successMessage.count()) === 0) {
    await page.waitForTimeout(500);
  }

  return { status: "updated", details: `Updated '${change.fieldName}'.` };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const baseUrl = (process.env.OSHUB_ADMIN_BASE_URL || "https://opensupplyhub.org").replace(/\/+$/, "");

  const csvPath = path.resolve(process.cwd(), args.csv);
  if (!fs.existsSync(csvPath)) {
    throw new Error(`CSV file not found: ${csvPath}`);
  }

  const { changes, stats } = loadChanges(csvPath, args.assignee, args.includeDone);
  console.log(
    `CSV stats: total=${stats.totalRows}, assignee=${stats.matchedAssignee}, after_status_filter=${stats.matchedStatus}, actionable=${stats.actionable}`
  );

  if (args.checkCsv) {
    console.log("CSV check mode enabled. No login/update will be performed.");
    return;
  }

  const email = process.env.OSHUB_ADMIN_EMAIL;
  const password = process.env.OSHUB_ADMIN_PASSWORD;

  if (!email || !password) {
    throw new Error("Set OSHUB_ADMIN_EMAIL and OSHUB_ADMIN_PASSWORD in env/.env.");
  }

  if (changes.length === 0) {
    console.log("No matching rows found for the specified assignee/filter.");
    return;
  }

  console.log(`Loaded ${changes.length} change(s) for assignee '${args.assignee}'.`);
  if (args.dryRun) {
    console.log("Running in DRY RUN mode. No updates will be saved.");
  }

  const browser = await chromium.launch({ headless: args.headless });
  const context = await browser.newContext();
  const page = await context.newPage();

  const results = [];
  try {
    await login(page, baseUrl, email, password);

    for (const change of changes) {
      const result = await updateOne(page, baseUrl, change, args.dryRun);
      results.push({
        country_code: change.countryCode,
        field_name: change.fieldName,
        status: result.status,
        details: result.details,
      });
      console.log(
        `[${result.status}] ${change.countryCode} ${change.fieldName} - ${result.details}`
      );
    }
  } finally {
    await context.close();
    await browser.close();
  }

  const summary = results.reduce((acc, row) => {
    acc[row.status] = (acc[row.status] || 0) + 1;
    return acc;
  }, {});

  console.log("\nSummary:");
  for (const [status, count] of Object.entries(summary)) {
    console.log(`- ${status}: ${count}`);
  }
}

main().catch((error) => {
  console.error(`ERROR: ${error.message}`);
  process.exit(1);
});
