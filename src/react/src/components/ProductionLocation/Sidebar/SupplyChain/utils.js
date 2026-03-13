const PLURAL_MAP = {
    'Academic / Researcher / Journalist / Student':
        'Academics / Researchers / Journalists / Students',
    'Auditor / Certification Scheme / Service Provider':
        'Auditors / Certification Schemes / Service Providers',
    'Brand / Retailer': 'Brands / Retailers',
    'Civil Society Organization': 'Civil Society Organizations',
    'Facility / Factory / Manufacturing Group / Supplier / Vendor':
        'Facilities / Factories / Manufacturing Groups / Suppliers / Vendors',
    'Multi-Stakeholder Initiative': 'Multi-Stakeholder Initiatives',
    Union: 'Unions',
    Other: 'Others',
};

const pluralizeContributorType = (type, count) => {
    if (count === 1) return type;
    return PLURAL_MAP[type] || `${type}s`;
};

export default pluralizeContributorType;
