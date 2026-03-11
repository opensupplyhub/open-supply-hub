import React from 'react';
import LearnMoreLink from './Shared/LearnMoreLink/LearnMoreLink';

export const FIELD_CONFIG = Object.freeze({
    name: Object.freeze({
        label: 'Name',
        tooltipText: 'The complete name of this production location.',
    }),
    parent_company: Object.freeze({
        label: 'Parent Company',
        tooltipText:
            'The company or group that holds majority ownership for this production location.',
    }),
    sector: Object.freeze({
        label: 'Industry / Sectors',
        tooltipText:
            'The sector(s) that this location operates in. For example: Apparel, Electronics, Renewable Energy.',
    }),
    product_type: Object.freeze({
        label: 'Product Type(s)',
        tooltipText:
            'The type of products produced at this location. For example: Shirts, Laptops, Solar Panels.',
    }),
    processing_type: Object.freeze({
        label: 'Processing Type(s)',
        tooltipText:
            'The type of processing activities that take place at this location. For example: Printing, Tooling, Assembly.',
    }),
    facility_type: Object.freeze({
        label: 'Location Type(s)',
        tooltipText:
            'The type of location. For example: Final Product Assembly, Raw Materials Production or Processing.',
    }),
    number_of_workers: Object.freeze({
        label: 'Number of Workers',
        tooltipText:
            'The number or range of people employed at this location. For example: 100, 100-150.',
    }),
    native_language_name: Object.freeze({
        label: 'Name in Native Language',
        tooltipText:
            'The production location name in the local language if different from the English name.',
    }),
    duns_id: Object.freeze({
        label: 'DUNS ID',
        tooltipText: '',
    }),
    lei_id: Object.freeze({
        label: 'LEI ID',
        tooltipText: '',
    }),
    rba_id: Object.freeze({
        label: 'RBA ID',
        tooltipText: '',
    }),
    parent_company_os_id: Object.freeze({
        label: 'Parent Company OS ID',
        tooltipText: '',
    }),
    isic_4: Object.freeze({
        label: 'ISIC 4',
        tooltipText: '',
    }),
    status: Object.freeze({
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

export default FIELD_CONFIG;
