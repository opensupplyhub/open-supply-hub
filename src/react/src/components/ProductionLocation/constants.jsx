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
