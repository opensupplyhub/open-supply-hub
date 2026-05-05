import sortBy from 'lodash/sortBy';

const FIELD_ORDER = [
    'name_native_language',
    'website',
    'phone_number',
    'contact_email',
    'contact_name',
    'office_name',
    'office_address',
    'office_phone_number',
    'description',
    'certifications',
    'affiliations',
    'minimum_order',
    'average_lead_time',
    'female_workers_percentage',
    'estimated_annual_throughput',
    'actual_annual_energy_consumption',
    'opening_date',
    'closing_date',
    'sector',
    'facility_type',
    'product_types',
    'production_types',
    'parent_company',
    'workers_count',
];

const sortClaimFields = fields =>
    sortBy(fields, ({ key }) => {
        const position = FIELD_ORDER.indexOf(key);
        return position === -1 ? FIELD_ORDER.length : position;
    });

export default sortClaimFields;
