// The live check of a just-submitted claim (OSDEV-3805). Everything a
// claimant can be shown is written here: nothing is generated on the
// fly and nothing the API returns is rendered as text.

export const CLAIM_LIVE_CHECK_STATUSES = Object.freeze({
    CHECKING: 'CHECKING',
    PASSED: 'PASSED',
    NOT_PASSED: 'NOT_PASSED',
    UNAVAILABLE: 'UNAVAILABLE',
});

// The preset fixes, keyed as the API names them. `text` is the line
// shown. `targets` are CSS selectors for the field the fix is about on
// the pending claim edit page, most specific first: the first one that
// is on the page is the field the claimant is taken to.
const ADDRESS_PROOF_TARGETS = Object.freeze([
    'label[for="company-address-verification-documents"]',
    '#locationAddressVerificationMethod',
]);

export const CLAIM_LIVE_CHECK_FIXES = Object.freeze({
    work_email: Object.freeze({
        text: 'Use a work email, not a personal email.',
        targets: Object.freeze(['#claimant-email']),
    }),
    upload_document: Object.freeze({
        text: 'Upload a document. Claims with a document are approved fastest.',
        targets: ADDRESS_PROOF_TARGETS,
    }),
    unreadable_document: Object.freeze({
        text: 'A document could not be read. Upload a clearer photo or a PDF.',
        targets: ADDRESS_PROOF_TARGETS,
    }),
    name_and_company_document: Object.freeze({
        text:
            'Add a document that shows your name and your company. For example a business card, employment letter or ID badge.',
        targets: Object.freeze([
            'label[for="employment-verification-upload"]',
            '#claimantEmploymentVerificationMethod',
        ]),
    }),
    company_name_document: Object.freeze({
        text: 'Add an official document that shows the company name.',
        targets: ADDRESS_PROOF_TARGETS,
    }),
    company_address_document: Object.freeze({
        text:
            'Add an official document that shows the company address. For example a utility bill or business registration.',
        targets: ADDRESS_PROOF_TARGETS,
    }),
});

export const CHECK_AND_SUBMIT_BUTTON_TEXT = 'Check and submit my claim';
export const CHECK_AND_SUBMIT_HELPER_TEXT =
    'Submits the claim and checks it right away. Stay on this page for up to one minute. If it passes, the claim is approved. If it does not pass, you will see what to change. You can also leave it for a person to review.';
export const SAVE_AND_CHECK_AGAIN_BUTTON_TEXT = 'Save and check again';

export const CHECKING_TITLE = 'Checking your claim';
export const CHECKING_STAY_TEXT =
    'This takes up to one minute. Stay on this page.';
export const CHECKING_BAR_LABEL = 'Checking your claim';

// The steps shown while the check runs, and how long after the start
// each one becomes the current step. They are time-based for now: the
// review service does not report its stages yet. When it does, these
// can follow the real stages instead. The first step is finished
// before the check starts (the claim is already saved), and the last
// one stays in progress until the result arrives.
export const CHECKING_STEPS = Object.freeze([
    Object.freeze({ label: 'Claim submitted', startsAtMs: 0 }),
    Object.freeze({ label: 'Reading your documents', startsAtMs: 0 }),
    Object.freeze({
        label: 'Checking the company name and address',
        startsAtMs: 12000,
    }),
    Object.freeze({
        label: 'Checking your link to the company',
        startsAtMs: 30000,
    }),
]);

// The progress bar has no real signal either, so it follows the time
// passed on a curve that moves quickly at first and then slows: it is
// at CHECKING_BAR_ANCHOR_PERCENT after CHECKING_BAR_ANCHOR_MS and never
// goes past CHECKING_BAR_MAX_PERCENT until the result arrives.
export const CHECKING_BAR_ANCHOR_MS = 45000;
export const CHECKING_BAR_ANCHOR_PERCENT = 90;
export const CHECKING_BAR_MAX_PERCENT = 95;

// One fact is shown at a time while the claimant waits.
export const FACT_LABEL_LOCATION = 'About this location';
export const FACT_LABEL_APPROVED = 'When your claim is approved';
export const FACT_LABEL_GOOD_TO_KNOW = 'Good to know';
export const CHECKING_FACTS = Object.freeze([
    Object.freeze({
        label: FACT_LABEL_APPROVED,
        text:
            'Your profile shows a Claimed badge. Buyers can see the details come from you.',
    }),
    Object.freeze({
        label: FACT_LABEL_APPROVED,
        text:
            'You can add your certifications, number of workers and product types.',
    }),
    Object.freeze({
        label: FACT_LABEL_GOOD_TO_KNOW,
        text: 'You can leave this page. The result is also sent by email.',
    }),
]);
export const FACT_INTERVAL_MS = 5000;

// How often the bar and the steps are redrawn, and how long the
// finished bar and steps stay up before the result replaces them.
export const WAITING_TICK_MS = 250;
export const RESULT_HOLD_MS = 600;

export const PASSED_TITLE = 'Your claim is approved.';

export const NOT_PASSED_TITLE = 'Your claim did not pass the pre-check.';
export const FIX_THIS_LABEL = 'Fix this:';
export const CHOOSE_ONE_LABEL = 'Choose one:';
export const GO_BACK_BUTTON_TEXT = 'Go back and fix it';
export const GO_BACK_HELPER_TEXT =
    'Opens the exact field to change. Then check again.';
// Shown instead once the claim has used all its checks.
export const GO_BACK_NO_CHECKS_HELPER_TEXT = 'Opens the exact field to change.';
export const LEAVE_BUTTON_TEXT = 'Leave it for review';
export const LEAVE_HELPER_TEXT =
    'A person will review the claim. Approval can be significantly delayed.';

export const UNAVAILABLE_TITLE = 'The pre-check is not available right now.';
export const UNAVAILABLE_TEXT =
    'Your claim is submitted. A person will review it.';
export const UNAVAILABLE_EMAIL_TEXT =
    'You will get an email when the claim is reviewed.';

// Space kept between the site's fixed top menu and the result panel
// when the panel is scrolled into view.
export const PANEL_SCROLL_MARGIN_PX = 24;

export const LEFT_FOR_REVIEW_TITLE =
    'Your claim is waiting for a person to review it.';

// How often the page asks for the answer and how long it keeps asking.
// The API gives up on a check after the same minute.
export const POLL_INTERVAL_MS = 3000;
export const CHECK_TIMEOUT_MS = 60000;

// Query parameters that carry a "go back and fix it" choice to the
// pending claim edit page.
export const FIX_QUERY_PARAM = 'fix';
export const CHECK_AGAIN_QUERY_PARAM = 'check';
