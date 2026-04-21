import React from 'react';
import PropTypes from 'prop-types';
import cloneDeep from 'lodash/cloneDeep';
import get from 'lodash/get';
import { formatExtendedField } from '../../../../util/util.js';
import { GA_LINK_PLACEMENT } from '../../../../util/analytics/gaCustomEvents';
import FacilityDetailsItem from '../../../FacilityDetailsItem.jsx';
import PartnerFieldSchemaValue from '../../../PartnerFields/PartnerFieldSchemaValue/PartnerFieldSchemaValue.jsx';
import ContributorLink from './ContributorLink';

const renderPartnerFieldValue = (
    formatted,
    partnerConfigFields,
    item,
    linkPlacement,
    partnerGroupName,
    osId,
    resolvedLabel,
) => {
    if (formatted.jsonSchema) {
        return (
            <PartnerFieldSchemaValue
                value={formatted.primary}
                jsonSchema={formatted.jsonSchema}
                partnerConfigFields={partnerConfigFields}
                gaSpotlightAnalytics={
                    partnerGroupName
                        ? {
                              link_placement: linkPlacement,
                              partner_group: partnerGroupName,
                              os_id: String(osId ?? ''),
                              partner_field_name: resolvedLabel,
                              contributor_name: item.contributor_name,
                              user_id:
                                  item.contributor_id != null
                                      ? String(item.contributor_id)
                                      : '',
                          }
                        : undefined
                }
            />
        );
    }
    return formatted.primary;
};

const toContributionCard = (
    item,
    formatField,
    partnerConfigFields,
    partnerGroupName,
    osId,
    resolvedLabel,
) => {
    const formatted = formatField(item);
    return {
        value: renderPartnerFieldValue(
            formatted,
            partnerConfigFields,
            item,
            GA_LINK_PLACEMENT.CONTRIBUTIONS_DRAWER,
            partnerGroupName,
            osId,
            resolvedLabel,
        ),
        sourceName: item.contributor_name,
        date: item.created_at,
        userId: item.contributor_id,
    };
};

export default function PartnerFieldItem({
    field: { fieldName, formatValue, label, partnerConfigFields },
    facilityData,
    partnerGroupName,
}) {
    const values = get(
        facilityData,
        `properties.partner_fields.${fieldName}`,
        [],
    );

    const osId = get(facilityData, 'properties.os_id', '') ?? '';

    if (!values.length || !values[0]) return null;

    const formatField = item => {
        const formatted = formatExtendedField({
            ...item,
            formatValue,
        });
        const itemLabel = formatted.label ? formatted.label : label;
        return {
            ...formatted,
            secondary: (
                <ContributorLink
                    {...item}
                    gaSpotlightContext={
                        partnerGroupName
                            ? {
                                  partner_group: partnerGroupName,
                                  os_id: String(osId ?? ''),
                                  partner_field_name: itemLabel,
                              }
                            : null
                    }
                />
            ),
        };
    };

    const topItem = cloneDeep(values[0]);
    const topValue = {
        ...formatField(topItem),
    };
    const additionalContent = values.slice(1).map(formatField);
    const resolvedLabel = topValue.label ? topValue.label : label;

    const gaSpotlightAnalyticsPrimary =
        partnerGroupName && topValue.jsonSchema
            ? {
                  link_placement: GA_LINK_PLACEMENT.CONTRIBUTION_LINE,
                  partner_group: partnerGroupName,
                  os_id: String(osId ?? ''),
                  partner_field_name: resolvedLabel,
                  contributor_name: topItem.contributor_name,
                  user_id:
                      topItem.contributor_id != null
                          ? String(topItem.contributor_id)
                          : '',
              }
            : undefined;

    const spotlightGaProfileBase = partnerGroupName
        ? {
              partner_group: partnerGroupName,
              os_id: String(osId ?? ''),
              partner_field_name: resolvedLabel,
          }
        : null;

    return (
        <FacilityDetailsItem
            {...topValue}
            label={resolvedLabel}
            additionalContent={additionalContent}
            partnerConfigFields={partnerConfigFields}
            customDrawer
            drawerFieldName={resolvedLabel}
            gaSpotlightAnalytics={gaSpotlightAnalyticsPrimary}
            spotlightGaProfileBase={spotlightGaProfileBase}
            drawerPromotedContribution={
                additionalContent.length > 0
                    ? toContributionCard(
                          topItem,
                          formatField,
                          partnerConfigFields,
                          partnerGroupName,
                          osId,
                          resolvedLabel,
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
                                  partnerGroupName,
                                  osId,
                                  resolvedLabel,
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
    partnerGroupName: PropTypes.string,
};

PartnerFieldItem.defaultProps = {
    facilityData: null,
    partnerGroupName: null,
};
