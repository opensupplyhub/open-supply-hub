const EMPLOYMENT_VERIFICATION_OPTIONS = Object.freeze([
    {
        value: 'employment-letter',
        label:
            'Employment letter or contract showing your name, title, and company',
    },
    {
        value: 'signed-company-letter',
        label:
            'Signed and/or stamped letter on company letterhead that confirms your name, your title with the company, and your email address',
    },
    {
        value: 'id-badge',
        label: 'Company ID badge or access card (photo showing name and title)',
    },
    {
        value: 'org-chart',
        label: 'Official organizational chart showing your position',
    },
    {
        value: 'business-card',
        label: 'Business card showing your name, title and company',
    },
    {
        value: 'company-website-address',
        label:
            'Company website showing your name and title (e.g., About Us, Team page)',
    },
    {
        value: 'official-company-document',
        label: 'An official company document showing your name and title',
    },
    {
        value: 'audit-reports',
        label: 'Audit reports showing your name and role at the facility',
    },
    {
        value: 'linkedin-page',
        label: 'Your LinkedIn page showing your name, title and company',
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
