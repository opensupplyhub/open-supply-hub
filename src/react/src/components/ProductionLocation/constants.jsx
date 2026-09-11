import React from 'react';
import { Link } from 'react-router-dom';
import LearnMoreLink from './Shared/LearnMoreLink/LearnMoreLink';
import { productionLocationsRoute } from '../../util/constants';

export const FIELD_CONFIG = Object.freeze({
    name: Object.freeze({
        key: 'name',
        label: 'Name',
        tooltipText: 'The complete name of this production location.',
    }),
    address: Object.freeze({
        key: 'address',
        label: 'Address',
        tooltipText: 'The company address for this production location.',
    }),
    coordinates: Object.freeze({
        key: 'coordinates',
        label: 'Coordinates',
        tooltipText:
            "The geographic coordinates (latitude, longitude) of this production location generated with Google's geocoding API.",
    }),
    parent_company: Object.freeze({
        key: 'parent_company',
        label: 'Parent Company',
        tooltipText:
            'The company or group that holds majority ownership for this production location.',
    }),
    sector: Object.freeze({
        key: 'sector',
        label: 'Industry / Sectors',
        tooltipText:
            'The sector(s) that this location operates in. For example: Apparel, Electronics, Renewable Energy.',
    }),
    product_type: Object.freeze({
        key: 'product_type',
        label: 'Product Type(s)',
        tooltipText:
            'The type of products produced at this location. For example: Shirts, Laptops, Solar Panels.',
    }),
    processing_type: Object.freeze({
        key: 'processing_type',
        label: 'Processing Type(s)',
        tooltipText:
            'The type of processing activities that take place at this location. For example: Printing, Tooling, Assembly.',
    }),
    facility_type: Object.freeze({
        key: 'facility_type',
        label: 'Location Type(s)',
        tooltipText:
            'The type of location. For example: Final Product Assembly, Raw Materials Production or Processing.',
    }),
    number_of_workers: Object.freeze({
        key: 'number_of_workers',
        label: 'Number of Workers',
        tooltipText:
            'The number or range of people employed at this location. For example: 100, 100-150.',
    }),
    native_language_name: Object.freeze({
        key: 'native_language_name',
        label: 'Name in Native Language',
        tooltipText:
            'The production location name in the local language if different from the English name.',
    }),
    duns_id: Object.freeze({
        key: 'duns_id',
        label: 'DUNS ID',
        tooltipText:
            'The Dun & Bradstreet unique nine-digit identifier used to track and verify business entities globally.',
    }),
    lei_id: Object.freeze({
        key: 'lei_id',
        label: 'LEI ID',
        tooltipText:
            'The Legal Entity Identifier, a globally unique code used to identify legally registered organizations participating in financial transactions.',
    }),
    rba_id: Object.freeze({
        key: 'rba_id',
        label: 'RBA ID',
        tooltipText:
            'The Responsible Business Alliance unique identifier assigned to this production location for auditing, assessment and membership records.',
    }),
    parent_company_os_id: Object.freeze({
        key: 'parent_company_os_id',
        label: 'Parent Company OS ID',
        tooltipText:
            'The Open Supply Hub identifier for the parent company that owns or controls this production location. Links to the parent company profile.',
    }),
    isic_4: Object.freeze({
        key: 'isic_4',
        label: 'ISIC 4',
        tooltipText:
            'The International Standard Industrial Classification (ISIC Rev. 4) code as defined by the United Nations indicating the primary economic activity of this production location based on the ISIC taxonomy classification.',
    }),
    status: Object.freeze({
        key: 'status',
        label: 'Closure Status',
        tooltipText: (
            <>
                Indicates whether this production location has been reported as
                closed by a supply chain network member, or verified as closed
                by the OS Hub team. Verified closures have been confirmed
                through our review process.{' '}
                <LearnMoreLink href="https://open-supply.files.svdcdn.com/production/assets/downloads/Open-Supply-Hub-Policy_-Marking-facilities-as-closed.pdf?dm=1667241212">
                    Learn more →
                </LearnMoreLink>
            </>
        ),
    }),
});

/** Display order for General Information section fields. */
export const ORDERED_GENERAL_FIELD_KEYS = Object.freeze([
    FIELD_CONFIG.name.key,
    FIELD_CONFIG.parent_company.key,
    FIELD_CONFIG.sector.key,
    FIELD_CONFIG.product_type.key,
    FIELD_CONFIG.facility_type.key,
    FIELD_CONFIG.processing_type.key,
    FIELD_CONFIG.number_of_workers.key,
    FIELD_CONFIG.native_language_name.key,
    FIELD_CONFIG.parent_company_os_id.key,
    FIELD_CONFIG.isic_4.key,
    FIELD_CONFIG.rba_id.key,
    FIELD_CONFIG.duns_id.key,
    FIELD_CONFIG.lei_id.key,
    FIELD_CONFIG.status.key,
]);

/**
 * Data-center-only attribute fields, grouped for the details page
 * (OSDEV-3076 / OSDEV-3077). Rendered only when `properties.is_data_center`
 * is true, additively below the shared General Information section. Provenance
 * fields are intentionally excluded (they live on FacilityListItem, not on
 * extended_fields). Each field reads `properties.extended_fields.<key>`;
 * `unitsField` combines a measure with its units into one displayed value
 * (e.g. "20 MW") and must only be set when the backend actually defines that
 * `<key>_units` field, otherwise the value renders as "(No unit specified)".
 *
 * Each group carries a `description` used as the section tooltip; keep it in
 * sync with `getDataCenterFieldGroups`, which forwards it to the details page.
 */
export const DATA_CENTER_FIELD_GROUPS = Object.freeze([
    Object.freeze({
        label: 'Named Entities',
        description:
            'Includes the organizations connected to this location: who operates it, who owns it, who manages the property, and who holds the permits.',
        fields: Object.freeze([
            {
                key: 'name_operator',
                label: 'Operator',
                tooltipText:
                    'The entity that operates this location.',
            },
            {
                key: 'name_owner',
                label: 'Owner',
                tooltipText: 'The entity that owns this location.',
            },
            {
                key: 'name_property_manager',
                label: 'Property Manager',
                tooltipText:
                    'The entity responsible for managing the property.',
            },
            {
                key: 'name_building_owner',
                label: 'Building Owner',
                tooltipText:
                    'The entity that owns the building where this location is situated.',
            },
            {
                key: 'name_tenant',
                label: 'Tenant',
                tooltipText:
                    'The entity that leases or rents out the space at this location.',
            },
            {
                key: 'name_permit_holder',
                label: 'Permit Holder',
                tooltipText:
                    'An entity that holds the permit(s) to operate at this location.',
            },
            {
                key: 'name_site_other',
                label: 'Other Site Name',
                tooltipText:
                    'An alternative name for this production location.',
            },
            {
                key: 'name_unspecified',
                label: 'Other Named Entity',
                tooltipText:
                    'A named entity that has a documented relationship with this location, but the nature of the relationship is not clear.',
            },
        ]),
    }),
    Object.freeze({
        label: 'Utility Usage',
        description:
            'Utilities: how much power, fuel, or water this location uses, power/water/fuel sources, and measures of efficiency.',
        fields: Object.freeze([
            {
                key: 'capacity',
                label: 'Capacity',
                unitsField: 'capacity_units',
                tooltipText:
                    'How much electrical power the data center(s) can use at once. There are different ways to measure capacity, and this general "capacity" field is only used when the type of capacity is not specified.',
            },
            {
                key: 'it_capacity',
                label: 'IT Capacity',
                unitsField: 'it_capacity_units',
                tooltipText:
                    'How much electrical power the data center\'s computing equipment can use at once.',
            },
            {
                key: 'utility_capacity',
                label: 'Utility Capacity',
                unitsField: 'utility_capacity_units',
                tooltipText:
                    'How much electrical power the entire data center building or campus can use at once. Includes power for computing, cooling, and anything else power may be used for (for example, lighting).',
            },
            {
                key: 'ups_capacity',
                label: 'UPS Capacity',
                unitsField: 'ups_capacity_units',
                tooltipText:
                    'Uninterruptible power supply (UPS) capacity is how much backup electrical power is instantly available to the data center if it suddenly loses power. This instant backup power is typically from batteries that run until longer-running backup power sources (like diesel generators) start working.',
            },
            {
                key: 'backup_generator_capacity',
                label: 'Backup Generator Capacity',
                unitsField: 'backup_generator_capacity_units',
                tooltipText:
                    'The amount of electrical power the data center has available in backup generators if the data center loses its regular source of power.',
            },
            {
                key: 'pue',
                // PUE is a dimensionless ratio, so there is no `pue_units`
                // field on the backend and none should be displayed.
                label: 'Power Usage Effectiveness (PUE)',
                tooltipText:
                    'Power usage effectiveness (PUE) is the ratio of how much power the data center uses overall to how much power it uses on computing equipment specifically. For example, a PUE of 1.2 means that for every 1 MW of power the computing equipment uses, an additional 0.2 MW are needed for cooling equipment or other electrical needs. A lower PUE means a more energy-efficient data center.',
            },
            {
                key: 'power_providers',
                label: 'Power Providers',
                tooltipText:
                    'Entities that supply power to this location.',
            },
            {
                key: 'power_sources',
                label: 'Power Sources',
                tooltipText:
                    'Information about the power sources the location uses.',
            },
            {
                key: 'power_density',
                label: 'Power Density',
                unitsField: 'power_density_units',
                tooltipText:
                    'How concentrated a data center\'s electrical power use is within a given physical space. Typically measured as power per server rack or power per unit of floor area.',
            },
            {
                key: 'water_usage',
                label: 'Water Usage',
                unitsField: 'water_usage_units',
                tooltipText:
                    'The amount of water used by this location.',
            },
            {
                key: 'wue',
                unitsField: 'wue_units',
                label: 'Water Use Efficiency (WUE)',
                tooltipText:
                    'Water usage effectiveness (WUE) is the volume of water used per amount of energy used. Low WUE means greater water usage efficiency.',
            },
            {
                key: 'onsite_power_generation',
                label: 'On-site Power Generation',
                tooltipText:
                    'Power generated on-site at this location.',
            },
            {
                key: 'cooling_mechanism',
                label: 'Cooling Mechanism',
                tooltipText:
                    'Any information about cooling mechanism(s) the location uses.',
            },
        ]),
    }),
    Object.freeze({
        label: 'Operating Information',
        description:
            'Includes the current status of this location, when it became operational, the time zones it serves, and the certifications it holds.',
        fields: Object.freeze([
            {
                key: 'operational_status',
                label: 'Operational Status',
                tooltipText:
                    'The current status of the location as described in the source - for example, planned, built, operational, retired, etc.',
            },
            {
                key: 'date_operational',
                label: 'Operational Date',
                tooltipText:
                    'The date when this location became operational.',
            },
            {
                key: 'time_zones',
                label: 'Time Zone(s)',
                tooltipText:
                    'The time zone(s) the location operates in.',
            },
            {
                key: 'certifications_compliance',
                label: 'Certifications / Compliance',
                tooltipText:
                    'Any certifications or compliance information for this location.',
            },
        ]),
    }),
    Object.freeze({
        label: 'Building Information',
        description:
            'Covers the physical footprint of this location: floor and land area, the number of floors and buildings, and the equipment housed inside.',
        fields: Object.freeze([
            {
                key: 'area',
                label: 'Area',
                unitsField: 'area_units',
                tooltipText: 'The physical area of the data center. There are different ways to measure area, and this general "area" field is only used when the type of area is not specified.',
            },
            {
                key: 'data_area',
                label: 'Data Hall Area',
                unitsField: 'data_area_units',
                tooltipText:
                    'Area specific to computing or data processing.',
            },
            {
                key: 'non_data_area',
                label: 'Non-Data Area',
                unitsField: 'non_data_area_units',
                tooltipText:
                    'Area not used for computing or data processing.',
            },
            {
                key: 'floor_space',
                label: 'Floor Space',
                unitsField: 'floor_space_units',
                tooltipText:
                    'Used if source describes area as "floor space" with no other information.',
            },
            {
                key: 'number_of_floors',
                label: 'Number of Floors',
                tooltipText:
                    'The total number of floors in this location.',
            },
            {
                key: 'footprint',
                label: 'Footprint',
                unitsField: 'footprint_units',
                tooltipText:
                    'How much area the building covers on the ground, regardless of building height or total building area.',
            },
            {
                key: 'building_area',
                label: 'Building Area',
                unitsField: 'building_area_units',
                tooltipText:
                    'Area of the entire building.',
            },
            {
                key: 'land_area',
                label: 'Land Area',
                unitsField: 'land_area_units',
                tooltipText:
                    'The total land area the location occupies, not just the buildings or other structures.',
            },
            {
                key: 'other_area',
                label: 'Other Area',
                unitsField: 'other_area_units',
                tooltipText:
                    'Specific type of area of this location that does not clearly match any of our standard area categories.',
            },
            {
                key: 'other_area_notes',
                label: 'Other Area Notes',
                tooltipText:
                    'How the source describes the other area.',
            },
            {
                key: 'number_of_servers',
                label: 'Number of Servers',
                tooltipText:
                    'The total number of servers at this location.',
            },
            {
                key: 'number_of_racks',
                label: 'Number of Racks',
                tooltipText:
                    'The total number of racks at this location. A rack can contain multiple servers.',
            },
            {
                key: 'number_of_buildings',
                label: 'Number of Buildings',
                tooltipText:
                    'Number of buildings stated in the source.',
            },
        ]),
    }),
    Object.freeze({
        label: 'Grouping',
        description:
            'Covers how this location relates to a wider group of data centers, such as a building or a campus.',
        fields: Object.freeze([
            {
                key: 'is_group',
                label: 'Is a Group',
                // Yes/no question - rendered as a checkbox in the SLC form.
                isBoolean: true,
                tooltipText:
                    'Indicates whether this record represents a group of data centers rather than a single one.',
            },
            {
                key: 'data_center_group_id',
                label: 'Group ID',
                tooltipText:
                    'The OSID of the group (building or campus) that this data center belongs to. Links to the group.',
                /*
                The value is the OS ID of the group's production location, so
                it is rendered as a link to that profile on the current
                server (OSDEV-3233).
                */
                renderValue: value => (
                    <Link to={`${productionLocationsRoute}/${value}`}>
                        {value}
                    </Link>
                ),
            },
        ]),
    }),
]);

export const NO_UNIT_SPECIFIED = '(No unit specified)';
