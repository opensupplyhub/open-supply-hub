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

export const CHECKING_PROGRESS_LINES = Object.freeze([
    'Checking your email.',
    'Reading your documents.',
    'Checking the company name and address.',
]);
export const CHECKING_STAY_TEXT =
    'Stay on this page. This takes up to one minute.';
export const CHECKING_EMAIL_TEXT =
    'If you leave this page, the result is sent to you by email.';

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

// How often the page asks for the answer, how long it keeps asking,
// and how often the progress line moves on. The API gives up on a
// check after the same minute.
export const POLL_INTERVAL_MS = 3000;
export const CHECK_TIMEOUT_MS = 60000;
export const PROGRESS_LINE_INTERVAL_MS = 6000;

// Query parameters that carry a "go back and fix it" choice to the
// pending claim edit page.
export const FIX_QUERY_PARAM = 'fix';
export const CHECK_AGAIN_QUERY_PARAM = 'check';
