export const COMPANY_ADDRESS_VERIFICATION_OPTIONS = Object.freeze([
    {
        value: 'company-website-address',
        label:
            'Company website showing the production location address (e.g., Contact Us, Locations page)',
    },
    {
        value: 'linkedin-address',
        label: 'Company LinkedIn page showing the production location address',
    },
    {
        value: 'utility-bill',
        label: 'Utility bill showing company name and address',
    },
    {
        value: 'business-registration',
        label: 'Business registration document',
    },
    {
        value: 'tax-license',
        label: 'Tax document or business license',
    },
    {
        value: 'property-lease',
        label: 'Property lease or ownership document',
    },
    {
        value: 'official-documents',
        label:
            'Upload other official documents (business registration, utility bills, etc.)',
    },
]);

export const URL_BASED_VERIFICATION_OPTIONS = Object.freeze([
    'company-website-address',
    'linkedin-address',
]);

export const DOCUMENT_BASED_VERIFICATION_OPTIONS = Object.freeze([
    'utility-bill',
    'business-registration',
    'tax-license',
    'property-lease',
    'official-documents',
]);
