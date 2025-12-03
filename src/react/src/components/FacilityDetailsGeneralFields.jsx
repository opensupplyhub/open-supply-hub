import React, { useMemo } from 'react';
import Grid from '@material-ui/core/Grid';
import get from 'lodash/get';
import isNil from 'lodash/isNil';
import filter from 'lodash/filter';
import { withStyles } from '@material-ui/core/styles';

import FacilityDetailsItem from './FacilityDetailsItem';
import FacilityDetailsClaimedInfo from './FacilityDetailsClaimedInfo/FacilityDetailsClaimedInfo';
import ShowOnly from './ShowOnly';
import FeatureFlag from './FeatureFlag';
import {
    formatAttribution,
    formatExtendedField,
    formatPartnerFieldValue,
} from '../util/util';

import {
    EXTENDED_FIELD_TYPES,
    ADDITIONAL_IDENTIFIERS,
    CLAIM_A_FACILITY,
    REPORT_A_FACILITY,
    SHOW_ADDITIONAL_IDENTIFIERS,
} from '../util/constants';

const locationFieldsStyles = theme =>
    Object.freeze({
        root: {
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
            borderTop: '2px solid #F9F7F7',
            borderBottom: '2px solid #F9F7F7',
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            paddingLeft: theme.spacing.unit * 3,
            paddingBottom: theme.spacing.unit * 3,
        },
    });

const formatActivityReports = data => {
    const reports = get(data, 'properties.activity_reports', []);
    if (!reports.length) return [null, []];
    const formattedReports = reports.reduce((list, r) => {
        let updatedList = [...list];
        if (r.status === 'CONFIRMED') {
            updatedList = [
                ...updatedList,
                {
                    primary: `Verified ${r.closure_state.toLowerCase()}`,
                    secondary: formatAttribution(r.status_change_date),
                    key: `${r.id}-verified}`,
                },
            ];
        }
        return [
            ...updatedList,
            {
                primary: `Reported ${r.closure_state.toLowerCase()}`,
                secondary: formatAttribution(
                    r.created_at,
                    r.reported_by_contributor,
                ),
                key: r.id,
            },
        ];
    }, []);
    return [formattedReports[0], formattedReports.slice(1)];
};

const FacilityDetailsGeneralFields = ({
    classes,
    data,
    nameField,
    otherNames,
    embed,
    embedConfig,
    hideSectorData,
    isClaimed,
}) => {
    const [sectorField, otherSectors] = useMemo(() => {
        const sectors = get(data, 'properties.sector', []).map(item => ({
            primary: item.values.join(', '),
            secondary: formatAttribution(
                item.created_at,
                item.contributor_name,
            ),
            isFromClaim: item.is_from_claim,
            key: item.contributor_id,
        }));
        return [sectors[0], sectors.slice(1)];
    }, [data]);

    const renderExtendedField = ({ label, fieldName, formatValue }) => {
        let values = get(data, `properties.extended_fields.${fieldName}`, []);

        const formatField = item =>
            formatExtendedField({ ...item, formatValue });

        if (fieldName === 'facility_type') {
            // Filter by values where a matched value has a facility_type field
            values = values.filter(v =>
                v?.value?.matched_values?.some(mv => mv[2]),
            );
        }

        if (!values.length || !values[0]) return null;

        if (fieldName === 'isic_4') {
            const groupedContributions = [];
            values.forEach(item => {
                const targetCount = item?.value_count || 1;
                const contributorKey =
                    item?.contributor_id ??
                    item?.contributor_name ??
                    item?.source_by ??
                    'unknown';
                const lastGroup =
                    groupedContributions[groupedContributions.length - 1];
                if (
                    lastGroup &&
                    lastGroup.contributorKey === contributorKey &&
                    lastGroup.remaining > 0
                ) {
                    lastGroup.items.push(item);
                    lastGroup.remaining -= 1;
                } else {
                    groupedContributions.push({
                        contributorKey,
                        remaining: targetCount - 1,
                        items: [item],
                    });
                }
            });

            const formattedGroups = groupedContributions
                .map(group => {
                    const formattedEntries = group.items
                        .map(formatField)
                        .filter(Boolean);

                    if (!formattedEntries.length) {
                        return null;
                    }

                    const primary = formattedEntries.reduce(
                        (acc, value, index) => {
                            if (index > 0) {
                                acc.push('');
                            }
                            if (Array.isArray(value.primary)) {
                                return acc.concat(value.primary);
                            }
                            acc.push(value.primary);
                            return acc;
                        },
                        [],
                    );

                    const groupKeyParts = [
                        fieldName,
                        group.contributorKey,
                        formattedEntries[0]?.secondary,
                        formattedEntries.length,
                    ]
                        .filter(Boolean)
                        .join('-');

                    return {
                        ...formattedEntries[0],
                        primary,
                        key: groupKeyParts,
                    };
                })
                .filter(Boolean);

            if (!formattedGroups.length) {
                return null;
            }

            const [topGroup, ...restGroups] = formattedGroups;

            return (
                <Grid item xs={12} md={6} key={fieldName}>
                    <FacilityDetailsItem
                        {...topGroup}
                        label={label}
                        additionalContent={restGroups}
                        additionalContentText="entry"
                        additionalContentTextPlural="entries"
                        embed={embed}
                    />
                </Grid>
            );
        }

        const topValue = formatField(values[0]);

        return (
            <Grid item xs={12} md={6} key={label}>
                <FacilityDetailsItem
                    {...topValue}
                    label={label}
                    additionalContent={values.slice(1).map(formatField)}
                    embed={embed}
                />
            </Grid>
        );
    };

    const renderContributorField = ({ label, value }) => {
        if (isNil(value) || value.toString().trim() === '') {
            return null;
        }
        return (
            <Grid item xs={12} md={6}>
                <FacilityDetailsItem
                    label={label}
                    primary={value}
                    key={label}
                />
            </Grid>
        );
    };

    const renderPartnerField = ({ label, fieldName, formatValue }) => {
        const values = get(data, `properties.partner_fields.${fieldName}`, []);

        const formatField = item =>
            formatExtendedField({
                ...item,
                formatValue,
            });

        if (!values.length || !values[0]) return null;

        const topValue = formatField(values[0]);

        return (
            <Grid item xs={12} md={6} key={`partner-${label}`}>
                <FacilityDetailsItem
                    {...topValue}
                    label={topValue.label ? topValue.label : label}
                    additionalContent={values.slice(1).map(formatField)}
                    embed={embed}
                />
            </Grid>
        );
    };

    const contributorFields = filter(
        get(data, 'properties.contributor_fields', null),
        field => field.value !== null,
    );
    const renderEmbedFields = () => {
        const fields = embedConfig?.embed_fields?.filter(f => f.visible) || [];
        return fields.map(({ column_name: fieldName, display_name: label }) => {
            // If there is an extended field for that name, render and return it
            const eft = EXTENDED_FIELD_TYPES.find(
                x => x.fieldName === fieldName,
            );
            const ef = eft ? renderExtendedField({ ...eft, label }) : null;
            if (ef) {
                return ef;
            }
            // Otherwise, try rendering it as a contributor field
            const cf = contributorFields.find(x => x.fieldName === fieldName);
            if (cf) {
                return renderContributorField(cf);
            }
            return null;
        });
    };

    const [activityReport, otherActivityReports] = useMemo(
        () => formatActivityReports(data),
        [data],
    );

    const renderExtendedFields = () => {
        const extendedFieldsWithoutAdditionalIdentifiers = EXTENDED_FIELD_TYPES.filter(
            field => !ADDITIONAL_IDENTIFIERS.includes(field.fieldName),
        );

        const partnerFieldNames = Object.keys(
            get(data, 'properties.partner_fields', {}),
        );

        const partnerFields = partnerFieldNames.map(fieldName => ({
            fieldName,
            label: fieldName
                .replace(/_/g, ' ')
                .replace(/\b\w/g, l => l.toUpperCase()),
            formatValue: formatPartnerFieldValue,
        }));

        return (
            <FeatureFlag
                flag={SHOW_ADDITIONAL_IDENTIFIERS}
                alternative={[
                    ...extendedFieldsWithoutAdditionalIdentifiers.map(
                        renderExtendedField,
                    ),
                    ...partnerFields.map(renderPartnerField),
                ]}
            >
                {EXTENDED_FIELD_TYPES.map(renderExtendedField)}
                {partnerFields.map(renderPartnerField)}
            </FeatureFlag>
        );
    };

    return (
        <div className={classes.root}>
            <div className={classes.contentContainer}>
                <Grid container>
                    <Grid item xs={12} md={6}>
                        <FacilityDetailsItem
                            {...nameField}
                            label="Name"
                            additionalContent={otherNames}
                            embed={embed}
                        />
                    </Grid>
                    {hideSectorData ? null : (
                        <Grid item xs={12} md={6}>
                            <FacilityDetailsItem
                                label="Sector"
                                {...sectorField}
                                additionalContent={otherSectors}
                                embed={embed}
                            />
                        </Grid>
                    )}
                    {embed ? renderEmbedFields() : renderExtendedFields()}
                    <FeatureFlag flag={REPORT_A_FACILITY}>
                        <ShowOnly when={!!activityReport}>
                            <FacilityDetailsItem
                                label="Status"
                                {...activityReport}
                                additionalContent={otherActivityReports}
                                additionalContentText="status"
                                additionalContentTextPlural="statuses"
                                embed={embed}
                            />
                        </ShowOnly>
                    </FeatureFlag>
                </Grid>
                <Grid container>
                    <FeatureFlag flag={CLAIM_A_FACILITY}>
                        <ShowOnly when={isClaimed}>
                            <FacilityDetailsClaimedInfo
                                data={data.properties.claim_info}
                            />
                        </ShowOnly>
                    </FeatureFlag>
                </Grid>
            </div>
        </div>
    );
};

export default withStyles(locationFieldsStyles)(FacilityDetailsGeneralFields);
