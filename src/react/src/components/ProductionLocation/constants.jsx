import React from 'react';
import LearnMoreLink from './Shared/LearnMoreLink/LearnMoreLink';

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
 * (e.g. "20 MW").
 */
export const DATA_CENTER_FIELD_GROUPS = Object.freeze([
    Object.freeze({
        label: 'Named Entities',
        fields: Object.freeze([
            {
                key: 'name_operator',
                label: 'Operator',
                tooltipText:
                    'The entity that operates this production location.',
            },
            {
                key: 'name_owner',
                label: 'Owner',
                tooltipText: 'The entity that owns this production location.',
            },
            {
                key: 'name_property_manager',
                label: 'Property Manager',
                tooltipText:
                    'The entity responsible for managing the property of this production location.',
            },
            {
                key: 'name_building_owner',
                label: 'Building Owner',
                tooltipText:
                    'The entity that owns the building where this production location is situated.',
            },
            {
                key: 'name_tenant',
                label: 'Tenant',
                tooltipText:
                    'The entity that leases or rents the space at this production location.',
            },
            {
                key: 'name_permit_holder',
                label: 'Permit Holder',
                tooltipText:
                    'The entity that holds the necessary permits for operating this production location.',
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
                    'A generic label for a named entity associated with this production location.',
            },
        ]),
    }),
    Object.freeze({
        label: 'Utility Usage',
        fields: Object.freeze([
            {
                key: 'capacity',
                label: 'Capacity',
                unitsField: 'capacity_units',
                tooltipText:
                    'The maximum output or production capacity of this production location.',
            },
            {
                key: 'it_capacity',
                label: 'IT Capacity',
                unitsField: 'it_capacity_units',
                tooltipText:
                    'The information technology capacity of this production location.',
            },
            {
                key: 'utility_capacity',
                label: 'Utility Capacity',
                unitsField: 'utility_capacity_units',
                tooltipText:
                    'The utility capacity of this production location, indicating the maximum amount of utility resources it can handle.',
            },
            {
                key: 'ups_capacity',
                label: 'UPS Capacity',
                unitsField: 'ups_capacity_units',
                tooltipText:
                    'The uninterruptible power supply capacity of this production location.',
            },
            {
                key: 'backup_generator_capacity',
                label: 'Backup Generator Capacity',
                unitsField: 'backup_generator_capacity_units',
                tooltipText:
                    'The backup generator capacity of this production location.',
            },
            {
                key: 'pue',
                unitsField: 'pue_units',
                label: 'Power Usage Effectiveness (PUE)',
                tooltipText:
                    'A metric indicating the energy efficiency of a data center, calculated as the ratio of total power used by the data center to the power delivered to the IT equipment.',
            },
            {
                key: 'power_providers',
                label: 'Power Providers',
                tooltipText:
                    'Entities that supply electrical power to this production location.',
            },
            {
                key: 'power_sources',
                label: 'Power Sources',
                tooltipText:
                    'The origins of the electrical power used by this production location.',
            },
            {
                key: 'power_density',
                label: 'Power Density',
                unitsField: 'power_density_units',
                tooltipText:
                    'The amount of power consumed per unit area of the production location.',
            },
            {
                key: 'water_usage',
                label: 'Water Usage',
                unitsField: 'water_usage_units',
                tooltipText:
                    'The amount of water used by this production location.',
            },
            {
                key: 'wue',
                unitsField: 'wue_units',
                label: 'Water Use Efficiency (WUE)',
                tooltipText:
                    'A metric indicating the water efficiency of this production location, calculated as the ratio of total water used to the amount of water delivered to the IT equipment.',
            },
            {
                key: 'cooling_mechanism',
                label: 'Cooling Mechanism',
                tooltipText:
                    'The method used to cool this production location.',
            },
        ]),
    }),
    Object.freeze({
        label: 'Operating Information',
        fields: Object.freeze([
            {
                key: 'operational_status',
                label: 'Operational Status',
                tooltipText:
                    'Indicates whether this production location is currently operational, under construction, or decommissioned.',
            },
            {
                key: 'date_operational',
                label: 'Operational Date',
                tooltipText:
                    'The date when this production location became operational.',
            },
            {
                key: 'time_zones',
                label: 'Time Zone(s)',
                tooltipText:
                    'The time zone(s) to which this production location belongs.',
            },
            {
                key: 'certifications_compliance',
                label: 'Certifications / Compliance',
                tooltipText:
                    'The certifications and compliance information for this production location.',
            },
        ]),
    }),
    Object.freeze({
        label: 'Building Information',
        fields: Object.freeze([
            {
                key: 'area',
                label: 'Area',
                unitsField: 'area_units',
                tooltipText: 'The total area of this production location.',
            },
            {
                key: 'data_area',
                label: 'Data Hall Area',
                unitsField: 'data_area_units',
                tooltipText:
                    'The area dedicated to data processing and storage within this production location.',
            },
            {
                key: 'floor_space',
                label: 'Floor Space',
                unitsField: 'floor_space_units',
                tooltipText:
                    'The total floor space available in this production location.',
            },
            {
                key: 'overall_area',
                label: 'Overall Area',
                unitsField: 'overall_area_units',
                tooltipText: 'The overall area of this production location.',
            },
            {
                key: 'other_area',
                label: 'Other Area',
                unitsField: 'other_area_units',
                tooltipText:
                    'The area of this production location that is not categorized as data, floor, or overall space.',
            },
            {
                key: 'other_area_notes',
                label: 'Other Area Notes',
                tooltipText:
                    'Additional information about the other area of this production location.',
            },
            {
                key: 'number_of_servers',
                label: 'Number of Servers',
                tooltipText:
                    'The total number of servers in this production location.',
            },
            {
                key: 'number_of_racks',
                label: 'Number of Racks',
                tooltipText:
                    'The total number of racks in this production location.',
            },
        ]),
    }),
]);

export const NO_UNIT_SPECIFIED = '(No unit specified)';
