const PLURAL_MAP = {
    'Brand / Retailer': 'Brand / Retailers',
    'Civil Society Organization': 'Civil Society Organizations',
    Auditor: 'Auditors',
    Government: 'Governments',
    'Multi-Stakeholder Initiative': 'Multi-Stakeholder Initiatives',
    Other: 'Others',
};

const pluralizeContributorType = (type, count) => {
    if (count === 1) return type;
    return PLURAL_MAP[type] || `${type}s`;
};

export default pluralizeContributorType;
