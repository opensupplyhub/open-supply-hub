import React from 'react';
import PropTypes from 'prop-types';
import cloneDeep from 'lodash/cloneDeep';
import get from 'lodash/get';
import { formatExtendedField } from '../../../../util/util.js';
import FacilityDetailsItem from '../../../FacilityDetailsItem.jsx';
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

    const topItem = cloneDeep(values[0]);
    const topValue = {
        ...formatField(topItem),
    };
    const additionalContent = values.slice(1).map(formatField);
    const resolvedLabel = topValue.label ? topValue.label : label;

    return (
        <FacilityDetailsItem
            {...topValue}
            label={resolvedLabel}
            additionalContent={additionalContent}
            partnerConfigFields={partnerConfigFields}
            customDrawer
            drawerFieldName={resolvedLabel}
            drawerPromotedContribution={
                additionalContent.length > 0
                    ? toContributionCard(
                          topItem,
                          formatField,
                          partnerConfigFields,
                      )
                    : undefined
            }
            drawerContributions={
                additionalContent.length > 0
                    ? values
                          .slice(1)
                          .map(item =>
                              toContributionCard(
                                  item,
                                  formatField,
                                  partnerConfigFields,
                              ),
                          )
                    : undefined
            }
        />
    );
}

const partnerConfigFieldsPropType = PropTypes.oneOfType([
    PropTypes.shape({
        baseUrl: PropTypes.string,
        displayText: PropTypes.string,
    }),
    PropTypes.oneOf([null]),
]);

PartnerFieldItem.propTypes = {
    field: PropTypes.shape({
        fieldName: PropTypes.string.isRequired,
        formatValue: PropTypes.func,
        label: PropTypes.string.isRequired,
        partnerConfigFields: partnerConfigFieldsPropType,
    }).isRequired,
    facilityData: PropTypes.object,
};

PartnerFieldItem.defaultProps = {
    facilityData: null,
};
