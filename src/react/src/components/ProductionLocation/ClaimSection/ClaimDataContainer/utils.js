import sortBy from 'lodash/sortBy';

const FIELD_ORDER = [
    'name_native_language',
    'website',
    'phone_number',
    'office_name',
    'office_address',
    'description',
    'certifications',
    'affiliations',
    'minimum_order',
    'average_lead_time',
    'female_workers_percentage',
    'estimated_annual_throughput',
    'actual_annual_energy_consumption',
];

const sortClaimFields = fields =>
    sortBy(fields, ({ key }) => {
        const position = FIELD_ORDER.indexOf(key);
        return position === -1 ? FIELD_ORDER.length : position;
    });

export default sortClaimFields;
