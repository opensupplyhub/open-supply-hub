import React from 'react';
import get from 'lodash/get';
import { formatExtendedField } from '../../../../util/util.js';
import FacilityDetailsItem from '../../../FacilityDetailsItem.jsx';
import DataPoint from '../../DataPoint/DataPoint.jsx';
import ContributionsDrawer from '../../ContributionsDrawer/ContributionsDrawer.jsx';
import useDrawerState from '../../hooks.js';
import PartnerFieldSchemaValue from '../../../PartnerFields/PartnerFieldSchemaValue/PartnerFieldSchemaValue.jsx';
import ContributorLink from './ContributorLink';

const renderPartnerFieldValue = (formatted, partnerConfigFields) => {
    if (formatted.jsonSchema) {
        return (
            <PartnerFieldSchemaValue
                value={formatted.primary}
                jsonSchema={formatted.jsonSchema}
                partnerConfigFields={partnerConfigFields}
            />
        );
    }
    return formatted.primary;
};

const toContributionCard = (item, formatField, partnerConfigFields) => {
    const formatted = formatField(item);
    return {
        value: renderPartnerFieldValue(formatted, partnerConfigFields),
        sourceName: item.contributor_name,
        date: item.created_at,
        userId: item.contributor_id,
    };
};

export default function PartnerFieldItem({
    field: { fieldName, formatValue, label, partnerConfigFields },
    facilityData,
    useProductionLocationPage,
}) {
    const values = get(
        facilityData,
        `properties.partner_fields.${fieldName}`,
        [],
    );

    const [, isDrawerOpen, openDrawer, closeDrawer] = useDrawerState(null);

    if (!values.length || !values[0]) return null;

    const formatField = item => {
        const formatted = formatExtendedField({
            ...item,
            formatValue,
        });
        return {
            ...formatted,
            secondary: <ContributorLink {...item} />,
        };
    };

    if (useProductionLocationPage && values.length > 1) {
        const topItem = values[0];
        const topFormatted = formatField(topItem);
        const promotedContribution = toContributionCard(
            topItem,
            formatField,
            partnerConfigFields,
        );
        const drawerData = {
            promotedContribution,
            contributions: values
                .slice(1)
                .map(item =>
                    toContributionCard(item, formatField, partnerConfigFields),
                ),
        };

        return (
            <>
                <DataPoint
                    label={topFormatted.label ? topFormatted.label : label}
                    value={renderPartnerFieldValue(
                        topFormatted,
                        partnerConfigFields,
                    )}
                    contributorName={topItem.contributor_name}
                    date={topItem.created_at}
                    drawerData={drawerData}
                    onOpenDrawer={openDrawer}
                    multiline
                />
                <ContributionsDrawer
                    open={isDrawerOpen}
                    onClose={closeDrawer}
                    fieldName={topFormatted.label ? topFormatted.label : label}
                    promotedContribution={drawerData.promotedContribution}
                    contributions={drawerData.contributions}
                />
            </>
        );
    }

    const topItem = Object.assign({}, values[0]);
    const topValue = {
        ...formatField(topItem),
    };

    return (
        <FacilityDetailsItem
            {...topValue}
            label={topValue.label ? topValue.label : label}
            additionalContent={values.slice(1).map(formatField)}
            partnerConfigFields={partnerConfigFields}
        />
    );
}
