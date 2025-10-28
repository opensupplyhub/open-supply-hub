const EMPLOYMENT_VERIFICATION_OPTIONS = Object.freeze([
    {
        value: 'employment_letter',
        label:
            'Employment letter or contract showing your name, title, and company',
    },
    {
        value: 'signed_company_letter',
        label:
            'Signed and/or stamped letter on company letterhead that confirms your name, your title with the company, and your email address',
    },
    {
        value: 'id_badge',
        label: 'Company ID badge or access card (photo showing name and title)',
    },
    {
        value: 'org_chart',
        label: 'Official organizational chart showing your position',
    },
    {
        value: 'business_card',
        label: 'Business card showing your name, title and company',
    },
    {
        value: 'company_website',
        label:
            'Company website showing your name and title (e.g., About Us, Team page)',
    },
    {
        value: 'official_company_document',
        label: 'An official company document showing your name and title',
    },
    {
        value: 'audit_reports',
        label: 'Audit reports showing your name and role at the facility',
    },
    {
        value: 'linkedin_page',
        label: 'Your LinkedIn page showing your name, title and company',
    },
]);

export default EMPLOYMENT_VERIFICATION_OPTIONS;
