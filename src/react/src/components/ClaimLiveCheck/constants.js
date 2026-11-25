export const CLAIM_LIVE_CHECK_STATUSES = Object.freeze({
    CHECKING: 'CHECKING',
    PASSED: 'PASSED',
    NOT_PASSED: 'NOT_PASSED',
    UNAVAILABLE: 'UNAVAILABLE',
});

export const CLAIM_LIVE_CHECK_FIELDS = Object.freeze({
    EMPLOYMENT: 'employment',
    ADDRESS: 'address',
});

export const CLAIM_LIVE_CHECK_FIELD_LABELS = Object.freeze({
    [CLAIM_LIVE_CHECK_FIELDS.EMPLOYMENT]: 'Employment verification',
    [CLAIM_LIVE_CHECK_FIELDS.ADDRESS]: 'Company address verification',
});

// The preset fixes, keyed as the API names them. `targets` are CSS
// selectors on the pending claim edit page: the claimant is taken to
// the first one that is on the page.
const ADDRESS_PROOF_TARGETS = Object.freeze([
    'label[for="company-address-verification-documents"]',
    '#locationAddressVerificationMethod',
]);

export const CLAIM_LIVE_CHECK_FIXES = Object.freeze({
    upload_document: Object.freeze({
        text: 'Upload a document. Claims with a document are approved fastest.',
        field: CLAIM_LIVE_CHECK_FIELDS.ADDRESS,
        targets: ADDRESS_PROOF_TARGETS,
    }),
    unreadable_document: Object.freeze({
        text: 'A document could not be read. Upload a clearer photo or a PDF.',
        field: CLAIM_LIVE_CHECK_FIELDS.ADDRESS,
        targets: ADDRESS_PROOF_TARGETS,
    }),
    name_and_company_document: Object.freeze({
        text:
            'Add a document that shows your name and your company. For example a business card, employment letter or ID badge.',
        field: CLAIM_LIVE_CHECK_FIELDS.EMPLOYMENT,
        targets: Object.freeze([
            'label[for="employment-verification-upload"]',
            '#claimantEmploymentVerificationMethod',
        ]),
    }),
    company_name_document: Object.freeze({
        text: 'Add an official document that shows the company name.',
        field: CLAIM_LIVE_CHECK_FIELDS.ADDRESS,
        targets: ADDRESS_PROOF_TARGETS,
    }),
    company_address_document: Object.freeze({
        text:
            'Add an official document that shows the company address. For example a utility bill or business registration.',
        field: CLAIM_LIVE_CHECK_FIELDS.ADDRESS,
        targets: ADDRESS_PROOF_TARGETS,
    }),
});

export const CHECK_AND_SUBMIT_BUTTON_TEXT = 'Submit and check my claim';
export const CHECK_AND_SUBMIT_HELPER_TEXT =
    'We check your claim right away. Stay for up to one minute to see your result.';
export const SAVE_AND_CHECK_AGAIN_BUTTON_TEXT = 'Save and check again';

export const CHECKING_TITLE =
    'We are checking your claim. Stay for your result.';
export const CHECKING_STAY_TEXT =
    'It takes up to one minute. If something needs a fix, you can fix it here and get approved faster.';
export const CHECKING_LEAVE_TEXT =
    'Have to leave? We will email your result. Fixing it later can delay your approval.';
export const CHECKING_BAR_LABEL = 'Checking your claim';

// The review service does not report its stages yet, so the steps
// follow the time passed since the check started.
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

export const FACT_LABEL_LOCATION = 'About this location';
export const FACT_LABEL_APPROVED = 'When your claim is approved';
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
]);
export const FACT_INTERVAL_MS = 5000;

export const WAITING_TICK_MS = 250;
export const RESULT_HOLD_MS = 600;

export const PASSED_TITLE = 'Your claim is approved.';

export const NOT_PASSED_TITLE =
    'Your claim is submitted, but it did not pass the check.';
export const makeFixLabel = count =>
    count === 1 ? 'Fix this:' : `Fix these ${count} things:`;
export const GO_BACK_BUTTON_TEXT = 'Update my claim';
export const CHOOSE_ONE_LABEL = 'Choose one:';
export const CHOICES_HELPER_TEXT =
    'Updating opens each field that needs a change. Skipping means a person reviews the claim, which can take much longer.';
export const CHOICES_NO_CHECKS_HELPER_TEXT =
    'Updating opens each field that needs a change. A person reviews the claim either way, which can take much longer.';
export const LEAVE_BUTTON_TEXT = 'Skip this and wait for a person to review';

export const UNAVAILABLE_TITLE = 'This is taking longer than usual.';
export const UNAVAILABLE_TEXT =
    'Your claim is submitted. You do not need to do anything.';
export const UNAVAILABLE_EMAIL_TEXT =
    'We will email you the result. If the check cannot finish, a person will review your claim.';

export const makeFixBannerTitle = count =>
    count === 1 ? '1 thing to fix' : `${count} things to fix`;

export const PANEL_SCROLL_MARGIN_PX = 24;

export const LEFT_FOR_REVIEW_TITLE =
    'Your claim is waiting for a person to review it.';

// The API gives up on a check after the same minute.
export const POLL_INTERVAL_MS = 3000;
export const CHECK_TIMEOUT_MS = 60000;

export const FIX_QUERY_PARAM = 'fix';
export const CHECK_AGAIN_QUERY_PARAM = 'check';
