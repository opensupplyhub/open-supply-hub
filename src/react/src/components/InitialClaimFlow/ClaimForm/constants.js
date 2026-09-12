export const CLAIM_FORM_STEPS = Object.freeze({
    ELIGIBILITY: 0,
    CONTACT: 1,
    BUSINESS: 2,
    PROFILE: 3,
});

export const STEP_NAMES = Object.freeze([
    'Eligibility Check',
    'Contact',
    'Business Information',
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
    'Please verify that this account is eligible to claim this production location.',
    'Provide your information and production location contact details.',
    'Verify the company address for this production location.',
    'Detailed information about the production location (Optional).',
]);

export const NEXT_BUTTON_TEXT = Object.freeze({
    [CLAIM_FORM_STEPS.ELIGIBILITY]: 'Continue',
    [CLAIM_FORM_STEPS.CONTACT]: 'Continue',
    [CLAIM_FORM_STEPS.BUSINESS]: 'Continue',
});

export const STEP_ICONS = Object.freeze({
    [CLAIM_FORM_STEPS.ELIGIBILITY]: 'Security',
    [CLAIM_FORM_STEPS.CONTACT]: 'People',
    [CLAIM_FORM_STEPS.BUSINESS]: 'Language',
    [CLAIM_FORM_STEPS.PROFILE]: 'Business',
});

export const TOTAL_STEPS = 4;

/**
 * Maps API/serializer field names to the labels shown on the Claim form UI.
 * Used when formatting server validation errors for the error banner.
 * Falls back to startCase(camelCase(field)) when a field is not listed.
 */
export const CLAIM_FORM_API_FIELD_LABELS = Object.freeze({
    facility_type: 'Location Type(s)',
    facility_product_types: 'Product Types',
    facility_production_types: 'Processing Type(s)',
    facility_description: 'Production Location Description',
    facility_phone_number: 'Company Phone',
    business_website: 'Company Website',
    local_language_name: 'Production Location Name in Native Language',
    parent_company_name: 'Parent Company Name / Supplier Group',
    office_official_name: 'Office Name',
    office_address: 'Office Address',
    office_country_code: 'Office Country',
    number_of_workers: 'Number of Workers',
    facility_female_workers_percentage: 'Percentage of Female Workers',
    facility_minimum_order_quantity: 'Minimum Order Quantity',
    facility_average_lead_time: 'Average Lead Time',
    facility_affiliations: 'Affiliations',
    facility_certifications: 'Certifications / Standards / Regulations',
    sectors: 'Industry / Sectors',
    your_name: 'Your Name',
    your_title: 'Your Job Title',
    your_business_website: 'Website URL',
});
