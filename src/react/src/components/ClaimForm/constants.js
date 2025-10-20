export const CLAIM_FORM_STEPS = Object.freeze({
    ELIGIBILITY: 0,
    CONTACT: 1,
    BUSINESS: 2,
    PROFILE: 3,
});

export const STEP_NAMES = Object.freeze([
    'Eligibility Check',
    'Contact',
    'Business',
    'Open Supply Hub Profile',
]);

export const STEP_SUBTITLES = Object.freeze([
    'Step 1',
    'Step 2',
    'Step 3',
    'Step 4',
]);

export const STEP_TIME_ESTIMATES = Object.freeze([
    '1 min',
    '5 mins',
    '3 mins',
    '10 mins',
]);

export const STEP_DESCRIPTIONS = Object.freeze([
    'Please verify that this account is eligible to claim this production location',
    'Provide your information and production location contact details',
    'Verify the company address for this production location',
    'Detailed information about the production location (Optional)',
]);

export const claimFormRoute = '/claim/:osID/details/';
export const claimIntroRoute = '/claim/:osID/';

// Map step indices to Material-UI icon names
export const STEP_ICONS = Object.freeze({
    [CLAIM_FORM_STEPS.ELIGIBILITY]: 'Security',
    [CLAIM_FORM_STEPS.CONTACT]: 'People',
    [CLAIM_FORM_STEPS.BUSINESS]: 'Language',
    [CLAIM_FORM_STEPS.PROFILE]: 'Business',
});

export const TOTAL_STEPS = 4;
