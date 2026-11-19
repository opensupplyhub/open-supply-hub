import { VERIFICATION_OPTION_TAGS } from '../../../Shared/VerificationOptionLabel/constants';

const { PREFERRED, CAN_DELAY } = VERIFICATION_OPTION_TAGS;

// `label` is the text stored on the claim
// (`claimant_employment_verification_method`), so it must not change.
// `tag` is the small tag shown beside an option in the dropdown, and is
// display only. The order (documents first, links last) only affects the
// dropdown.
const EMPLOYMENT_VERIFICATION_OPTIONS = Object.freeze([
    {
        value: 'employment-letter',
        label:
            'Employment letter or contract showing your name, title, and company',
        tag: PREFERRED,
    },
    {
        value: 'signed-company-letter',
        label:
            'Signed and/or stamped letter on company letterhead that confirms your name, your title with the company, and your email address',
        tag: PREFERRED,
    },
    {
        value: 'id-badge',
        label: 'Company ID badge or access card (photo showing name and title)',
        tag: PREFERRED,
    },
    {
        value: 'org-chart',
        label: 'Official organizational chart showing your position',
        tag: PREFERRED,
    },
    {
        value: 'business-card',
        label: 'Business card showing your name, title and company',
        tag: PREFERRED,
    },
    {
        value: 'official-company-document',
        label: 'An official company document showing your name and title',
        tag: PREFERRED,
    },
    {
        value: 'audit-reports',
        label: 'Audit reports showing your name and role at the facility',
        tag: PREFERRED,
    },
    {
        value: 'company-website-address',
        label:
            'Company website showing your name and title (e.g., About Us, Team page)',
        tag: CAN_DELAY,
    },
    {
        value: 'linkedin-page',
        label: 'Your LinkedIn page showing your name, title and company',
        tag: CAN_DELAY,
    },
]);

const EMPLOYMENT_URL_BASED_VERIFICATION_OPTIONS = Object.freeze([
    'company-website-address',
    'linkedin-page',
]);

const EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS = Object.freeze([
    'employment-letter',
    'signed-company-letter',
    'id-badge',
    'org-chart',
    'business-card',
    'official-company-document',
    'audit-reports',
]);

export {
    EMPLOYMENT_VERIFICATION_OPTIONS,
    EMPLOYMENT_URL_BASED_VERIFICATION_OPTIONS,
    EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS,
};
