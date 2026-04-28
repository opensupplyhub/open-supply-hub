# WageIndicator Admin Updater

Small Dockerized Playwright utility to update specific
`WageIndicatorCountryData` link fields in Django Admin.

It updates **only** rows from your CSV that match:

- `change_owner` (or `assignee`) equals the selected assignee
- `country_code` + `field_name` + `new_link` are present

Supported `field_name` values:

- `living_wage_link_national`
- `minimum_wage_link_english`
- `minimum_wage_link_national`

## 1) Prepare input CSV

Use a CSV with these columns (header names are flexible for old/new link):

- `country_code`
- `field_name`
- `old_link` or `old_links` (optional but recommended)
- `new_link` or `new_links`
- `change_owner` (or `assignee`)

Example file: `data/changes.example.csv`

## 2) Create `.env`

```bash
cp .env.example .env
```

Fill:

- `OSHUB_ADMIN_BASE_URL` (default `https://opensupplyhub.org`)
- `OSHUB_ADMIN_EMAIL`
- `OSHUB_ADMIN_PASSWORD`
- `OSHUB_ASSIGNEE_EMAIL` (default assignee filter, can be overridden by `--assignee`)

## 3) Build Docker image

```bash
docker build --no-cache -t wageindicator-admin-updater .
```

## 4) Run dry-run first (recommended)

```bash
docker run --rm --env-file .env \
  -v "$(pwd)/data:/app/data" \
  wageindicator-admin-updater \
  npm run update -- --csv data/changes.csv --dry-run
```

Validate CSV parsing only (no login needed):

```bash
docker run --rm --env-file .env \
  -v "$(pwd)/data:/app/data" \
  wageindicator-admin-updater \
  npm run update -- --csv "data/Copy of Wagenidicator Links Upd. - failed_links_detail.csv" --check-csv
```

## 5) Run real update

```bash
docker run --rm --env-file .env \
  -v "$(pwd)/data:/app/data" \
  wageindicator-admin-updater \
  npm run update -- --csv data/changes.csv
```

## Notes

- If `old_link` is provided and does not match the current admin value,
  the row is skipped with `old_link_mismatch` (safety check).
- Rows with `status=DONE` are skipped by default. Pass `--include-done`
  if you want to include them.
- If a country row is not found in admin search, it is reported as `not_found`.
- Use `--headed` instead of headless mode for debugging:

```bash
npm run update -- --csv data/changes.csv --headed
```
