import { VERIFICATION_OPTION_TAGS } from '../../../Shared/VerificationOptionLabel/constants';

const { PREFERRED, CAN_DELAY } = VERIFICATION_OPTION_TAGS;

// `label` is the text stored on the claim
// (`location_address_verification_method`), so it must not change. `tag`
// is the small tag shown beside an option in the dropdown, and is display
// only. The order (documents first, links last) only affects the dropdown.
export const COMPANY_ADDRESS_VERIFICATION_OPTIONS = Object.freeze([
    {
        value: 'utility-bill',
        label: 'Utility bill showing company name and address',
        tag: PREFERRED,
    },
    {
        value: 'business-registration',
        label: 'Business registration document',
        tag: PREFERRED,
    },
    {
        value: 'tax-license',
        label: 'Tax document or business license',
        tag: PREFERRED,
    },
    {
        value: 'property-lease',
        label: 'Property lease or ownership document',
        tag: PREFERRED,
    },
    {
        value: 'official-documents',
        label:
            'Upload other official documents (business registration, utility bills, etc.)',
        tag: PREFERRED,
    },
    {
        value: 'company-website-address',
        label:
            'Company website showing the production location address (e.g., Contact Us, Locations page)',
        tag: CAN_DELAY,
    },
    {
        value: 'linkedin-address',
        label: 'Company LinkedIn page showing the production location address',
        tag: CAN_DELAY,
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
