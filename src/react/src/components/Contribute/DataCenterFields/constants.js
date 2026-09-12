import camelCase from 'lodash/camelCase';

import { DATA_CENTER_FIELD_GROUPS } from '../../ProductionLocation/constants.jsx';
import { PROVENANCE_FIELD_LABELS } from '../../ProductionLocation/ContributionsDrawer/constants';

export const DATA_CENTER_TYPE_VALUE = 'Data Center';

const PROVENANCE_SECTION_LABEL = 'Source details';

/**
 * Short helper descriptions shown under each field label, keyed by the API
 * field key. Condensed from the data-center master dataset schema.
 */
const DATA_CENTER_FIELD_DESCRIPTIONS = Object.freeze({
    // Named entities
    name_operator:
        'Enter the entity described as the operator of the data center. ' +
        'For example: a colocation provider.',
    name_owner: 'Enter the entity described as the owner of the data center.',
    name_property_manager:
        'Enter the entity described as the property manager of the data ' +
        'center.',
    name_building_owner:
        'Enter the entity that owns the building, when different from the ' +
        'data center owner.',
    name_tenant: 'Enter an entity leasing space from the data center.',
    name_permit_holder:
        'Enter the entity named as the permit holder. For example: on ' +
        'government-issued air quality permits.',
    name_site_other: 'Enter an alternative or previous name for the same site.',
    name_unspecified:
        'Enter a name associated with the site when the relationship to the ' +
        'site is unclear.',
    // Utility usage
    capacity:
        'Enter the power capacity when the capacity type (IT, utility, UPS) ' +
        'is not specified by the source.',
    it_capacity:
        'Enter the maximum power available to IT equipment. Also referred ' +
        'to as critical power or IT load.',
    utility_capacity:
        'Enter the maximum power the data center can draw from the utility ' +
        'grid.',
    ups_capacity:
        'Enter the capacity of the uninterruptible power supply (UPS) ' +
        'system.',
    backup_generator_capacity: 'Enter the capacity of the backup generators.',
    pue:
        'Enter the Power Usage Effectiveness: the ratio of total energy ' +
        'used to energy delivered to computing equipment. For example: 1.25.',
    power_providers:
        'Enter the external power provider(s). For example: the local ' +
        'power authority or main private power company.',
    power_sources:
        'Enter the power source(s), including on-site generation. For ' +
        'example: coal, solar, wind.',
    power_density:
        'Enter the power density of the data center. For example: 150 ' +
        '(with units W/sq ft).',
    water_usage:
        'Enter the amount of water used, typically as volume per time. For ' +
        'example: 5000 (with units gallons per day).',
    wue:
        'Enter the Water Usage Effectiveness: a ratio measure of water ' +
        'use. For example: 1.8.',
    onsite_power_generation:
        'Enter any power generated on site, as stated by the source. For ' +
        'example: solar, on-site gas turbines.',
    cooling_mechanism:
        'Enter the cooling mechanism(s) used, as stated by the source. For ' +
        'example: air cooled, evaporative cooling.',
    // Operating information
    operational_status:
        'Enter the operational status as stated by the source. For ' +
        'example: planned, construction, operational, closed.',
    date_operational:
        'Enter when the data center became, or is planned to become, ' +
        'operational.',
    time_zones: 'Enter the time zone(s) the data center operates in.',
    certifications_compliance:
        'Enter any certifications or compliance information, as stated by ' +
        'the source.',
    // Building information
    area:
        'Enter the area when the area type (floor space, data hall) is not ' +
        'specified by the source.',
    data_area:
        'Enter the data or computing-specific area. Often referred to as ' +
        'data hall space or white space.',
    non_data_area: 'Enter the area not used for data processing or storage.',
    floor_space: 'Enter the floor space of the data center.',
    number_of_floors: 'Enter the number of floors, if known.',
    footprint: 'Enter the ground area occupied by the data center.',
    building_area: 'Enter the total area of the building.',
    land_area: 'Enter the total area of land the data center occupies.',
    other_area: 'Enter any other area not captured by the fields above.',
    other_area_notes: 'Describe the type of area entered in Other Area.',
    number_of_servers: 'Enter the number of servers, if known.',
    number_of_racks: 'Enter the number of racks, if known.',
    number_of_buildings: 'Enter the number of buildings, if known.',
    // Grouping
    is_group:
        'Set to true if this record represents a group of data centers ' +
        'rather than a single one.',
    data_center_group_id:
        'Enter the identifier of the group (building or campus) this data ' +
        'center belongs to. Used to link data centers in the same group.',
    // Source details (provenance)
    source_name:
        'Enter the name of the external source the data came from. For ' +
        'example: US EPA FRS, an operator website.',
    source_link:
        'Enter a link to the source page for this specific data center.',
    information_source_type:
        'Enter the type of source. For example: air quality permit, press ' +
        'release, company website.',
    date_of_source:
        'Enter the date stated by the source, at whatever precision is ' +
        'available: YYYY, YYYY-MM, or YYYY-MM-DD.',
    notes: 'Enter notes on any judgment calls made while collecting the data.',
    data_collection_methodology:
        'Enter how the data was collected. For example: copied from ' +
        'website, downloaded directly from source.',
    ai_usage_notes:
        'If AI was used, enter the model and version, the tasks it ' +
        'performed, and the extent of human review.',
});

/**
 * Form sections for the data-center SLC layout (OSDEV-3074), derived from the
 * display constants so the field list exists in one place. Formik field names
 * are the camelCase form of the API field keys, so `parseContribData`'s
 * generic snakeCase conversion maps them back to the exact v1 API keys.
 */
export const DATA_CENTER_FORM_SECTIONS = Object.freeze(
    [
        ...DATA_CENTER_FIELD_GROUPS.map(group => ({
            label: group.label,
            fields: group.fields.map(field => ({
                formName: camelCase(field.key),
                label: field.label,
                description: DATA_CENTER_FIELD_DESCRIPTIONS[field.key] || '',
                isCheckbox: !!field.isBoolean,
                unitsFormName: field.unitsField
                    ? camelCase(field.unitsField)
                    : null,
            })),
        })),
        {
            label: PROVENANCE_SECTION_LABEL,
            fields: PROVENANCE_FIELD_LABELS.map(field => ({
                formName: camelCase(field.key),
                label: field.label,
                description: DATA_CENTER_FIELD_DESCRIPTIONS[field.key] || '',
                isCheckbox: false,
                unitsFormName: null,
            })),
        },
    ].map(section => Object.freeze(section)),
);

/** Initial (empty) Formik values for every data-center form field. */
export const DATA_CENTER_FORM_INITIAL_VALUES = Object.freeze(
    DATA_CENTER_FORM_SECTIONS.reduce((acc, section) => {
        section.fields.forEach(field => {
            acc[field.formName] = '';
            if (field.unitsFormName) {
                acc[field.unitsFormName] = '';
            }
        });
        return acc;
    }, {}),
);

export const DATA_CENTER_FORM_FIELD_NAMES = Object.freeze(
    Object.keys(DATA_CENTER_FORM_INITIAL_VALUES),
);
