import React from 'react';
import get from 'lodash/get';
import { formatExtendedField } from '../../../../util/util.js';
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

    const topItem = values[0];
    const topFormatted = formatField(topItem);
    const resolvedLabel = topFormatted.label || label;
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
                label={resolvedLabel}
                value={renderPartnerFieldValue(
                    topFormatted,
                    partnerConfigFields,
                )}
                contributorName={topItem.contributor_name}
                userId={topItem.contributor_id}
                date={topItem.created_at}
                drawerData={drawerData}
                onOpenDrawer={openDrawer}
                multiline
            />
            <ContributionsDrawer
                open={isDrawerOpen}
                onClose={closeDrawer}
                fieldName={resolvedLabel}
                promotedContribution={drawerData.promotedContribution}
                contributions={drawerData.contributions}
            />
        </>
    );
}
