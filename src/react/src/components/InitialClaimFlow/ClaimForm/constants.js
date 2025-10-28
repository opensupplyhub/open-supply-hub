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

export const NEXT_BUTTON_TEXT = Object.freeze({
    [CLAIM_FORM_STEPS.ELIGIBILITY]: 'Continue to Contact Information',
    [CLAIM_FORM_STEPS.CONTACT]: 'Continue to Business Details',
    [CLAIM_FORM_STEPS.BUSINESS]: 'Continue to Production Location Details',
});

export const STEP_ICONS = Object.freeze({
    [CLAIM_FORM_STEPS.ELIGIBILITY]: 'Security',
    [CLAIM_FORM_STEPS.CONTACT]: 'People',
    [CLAIM_FORM_STEPS.BUSINESS]: 'Language',
    [CLAIM_FORM_STEPS.PROFILE]: 'Business',
});

export const TOTAL_STEPS = 4;

// Beta tooltip text for premium features
export const BETA_TOOLTIP_TEXT =
    "What does beta mean? Open Supply Hub is developing a Premium offering for facilities, to help you use your OS Hub profile to connect with more customers and build your business. Once live, all fields that say beta will be a part of this new package. For now, these beta fields will appear on your profile just like all the others. Once the Premium offering is live, you'll receive next steps about how it will work and whether you will want to keep these beta fields live.";

// Affiliations dropdown options
export const AFFILIATIONS_OPTIONS = [
    {
        value: 'benefits_for_business_and_workers',
        label: 'Benefits for Business and Workers (BBW)',
    },
    { value: 'better_mills_program', label: 'Better Mills Program' },
    { value: 'better_work', label: 'Better Work (ILO)' },
    { value: 'canopy', label: 'Canopy' },
    {
        value: 'ethical_trading_initiative',
        label: 'Ethical Trading Initiative',
    },
    { value: 'fair_labor_association', label: 'Fair Labor Association' },
    { value: 'fair_wear_foundation', label: 'Fair Wear Foundation' },
    { value: 'herfinance', label: 'HERfinance' },
    { value: 'herhealth', label: 'HERhealth' },
    { value: 'herrespect', label: 'HERrespect' },
    { value: 'sedex', label: 'SEDEX' },
    {
        value: 'social_and_labor_convergence_plan',
        label: 'Social and Labor Convergence Plan (SLCP)',
    },
    {
        value: 'sustainable_apparel_coalition',
        label: 'Sustainable Apparel Coalition',
    },
    {
        value: 'sweatfree_purchasing_consortium',
        label: 'Sweatfree Purchasing Consortium',
    },
    { value: 'zdhc', label: 'ZDHC' },
];

// Certifications dropdown options
export const CERTIFICATIONS_OPTIONS = [
    { value: 'bci', label: 'BCI' },
    { value: 'b_corp', label: 'B Corp' },
    { value: 'bluesign', label: 'Bluesign' },
    { value: 'canopy', label: 'Canopy' },
    { value: 'cradle_to_cradle', label: 'Cradle to Cradle' },
    { value: 'eu_ecolabel', label: 'EU Ecolabel' },
    { value: 'fairtrade_usa', label: 'Fairtrade USA' },
    { value: 'fsc', label: 'FSC' },
    {
        value: 'global_recycling_standard',
        label: 'Global Recycling Standard (GRS)',
    },
    { value: 'gots', label: 'GOTS' },
    { value: 'green_button', label: 'Green Button' },
    {
        value: 'green_screen_for_safer_chemicals',
        label: 'Green Screen for Safer Chemicals',
    },
    { value: 'higg_index', label: 'Higg Index' },
    { value: 'imo_control', label: 'IMO Control' },
    {
        value: 'international_wool_textile_organisation',
        label: 'International Wool Textile Organisation (IWTO)',
    },
    { value: 'iso_9000', label: 'ISO 9000' },
    { value: 'ivn_leather', label: 'IVN leather' },
    { value: 'leather_working_group', label: 'Leather Working Group' },
    { value: 'nordic_swan', label: 'Nordic Swan' },
    { value: 'oeko_tex_standard_100', label: 'Oeko-Tex Standard 100' },
    { value: 'oeko_tex_step', label: 'Oeko-Tex STeP' },
    { value: 'oeko_tex_eco_passport', label: 'Oeko-Tex Eco Passport' },
    { value: 'oeko_tex_made_in_green', label: 'Oeko-Tex Made in Green' },
    { value: 'pefc', label: 'PEFC' },
    { value: 'reach', label: 'REACH' },
    {
        value: 'responsible_down_standard',
        label: 'Responsible Down Standard (RDS)',
    },
    {
        value: 'responsible_wool_standard',
        label: 'Responsible Wool Standard (RWS)',
    },
    { value: 'sa8000', label: 'SA8000' },
    { value: 'abvtex', label: 'ABVTEX' },
    { value: 'empresa_b', label: 'Empresa B' },
    { value: 'origem_sustentavel', label: 'Origem Sustentável' },
    { value: 'selo_abr', label: 'Selo ABR' },
];
