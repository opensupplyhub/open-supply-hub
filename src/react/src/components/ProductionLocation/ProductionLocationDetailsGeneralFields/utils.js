import get from 'lodash/get';
import uniqBy from 'lodash/uniqBy';
import partition from 'lodash/partition';
import { formatAttribution, formatExtendedField } from '../../../util/util';
import renderUniqueListItems from '../../../util/renderUtils';
import {
    EXTENDED_FIELD_TYPES,
    ADDITIONAL_IDENTIFIERS,
} from '../../../util/constants';
import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from '../DataPoint/constants';
import FIELD_CONFIG from '../constants.jsx';

const toDrawerContribution = (item, valueStr) => ({
    value: valueStr,
    sourceName: item.contributor_name || item.source_by || null,
    date: item.created_at || null,
    userId: item.contributor_id != null ? item.contributor_id : undefined,
});

const getStatusLabel = isFromClaim =>
    isFromClaim ? STATUS_CLAIMED : STATUS_CROWDSOURCED;

const filterByUniqueField = (data, extendedFieldName) =>
    uniqBy(
        get(data, `properties.extended_fields.${extendedFieldName}`, []).map(
            formatExtendedField,
        ),
        item => item.primary + item.secondary,
    );

const formatActivityReports = data => {
    const reports = get(data, 'properties.activity_reports', []);
    if (!reports.length) return [];
    const items = reports.reduce((list, report) => {
        let updatedList = [...list];
        if (report.status === 'CONFIRMED') {
            updatedList = [
                ...updatedList,
                {
                    primary: `Verified ${report.closure_state.toLowerCase()}`,
                    date: report.status_change_date,
                    sourceName: null,
                },
            ];
        }
        return [
            ...updatedList,
            {
                primary: `Reported ${report.closure_state.toLowerCase()}`,
                date: report.created_at,
                sourceName: report.reported_by_contributor || null,
            },
        ];
    }, []);
    return items;
};

const getOrderedFieldConfigs = includeAdditionalIdentifiers => {
    const extendedTypes = includeAdditionalIdentifiers
        ? EXTENDED_FIELD_TYPES
        : EXTENDED_FIELD_TYPES.filter(
              fieldType =>
                  !ADDITIONAL_IDENTIFIERS.includes(fieldType.fieldName),
          );

    const nameConfig = {
        key: 'name',
        getDataPointProps: data => {
            if (!data) return null;
            const coreName = get(data, 'properties.name', '');
            const createdFrom = formatAttribution(
                get(data, 'properties.created_from.created_at', ''),
                get(data, 'properties.created_from.contributor', ''),
            );
            const nameFields = filterByUniqueField(data, 'name');
            const [defaultNameField, otherNameFields] = partition(
                nameFields,
                field => field.primary === coreName,
            );
            const top = defaultNameField.length
                ? defaultNameField[0]
                : {
                      primary: coreName,
                      secondary: createdFrom,
                  };
            const rawNameValues = get(
                data,
                'properties.extended_fields.name',
                [],
            );
            const topPrimary = top.primary;
            const topRaw =
                rawNameValues.find(
                    rawItem =>
                        formatExtendedField(rawItem).primary === topPrimary ||
                        (typeof rawItem.value === 'string'
                            ? rawItem.value
                            : rawItem.value?.name ||
                              rawItem.value?.raw_value) === topPrimary,
                ) ||
                rawNameValues[0] ||
                null;
            const promotedContribution =
                topRaw &&
                (() => {
                    const val =
                        typeof topRaw.value === 'string'
                            ? topRaw.value
                            : topRaw.value?.name || topRaw.value?.raw_value;
                    return toDrawerContribution(
                        topRaw,
                        val != null ? String(val) : '',
                    );
                })();
            const contributions = otherNameFields.map(field => {
                const rawItem = rawNameValues.find(raw => {
                    const formatted = formatExtendedField(raw);
                    return (
                        formatted.primary === field.primary &&
                        formatted.secondary === field.secondary
                    );
                });
                const valueStr =
                    field.primary != null ? String(field.primary) : '';
                return rawItem
                    ? toDrawerContribution(rawItem, valueStr)
                    : {
                          value: valueStr,
                          sourceName: null,
                          date: null,
                          userId: undefined,
                      };
            });
            const drawerData =
                promotedContribution || contributions.length
                    ? {
                          promotedContribution,
                          contributions,
                      }
                    : null;
            return {
                label: FIELD_CONFIG.name.label,
                value: top.primary,
                tooltipText: FIELD_CONFIG.name.tooltipText,
                statusLabel: getStatusLabel(top.isFromClaim),
                contributorName: topRaw
                    ? topRaw.contributor_name || null
                    : get(data, 'properties.created_from.contributor', null),
                userId: topRaw ? topRaw.contributor_id : null,
                date: topRaw
                    ? topRaw.created_at
                    : get(data, 'properties.created_from.created_at', null),
                drawerData,
            };
        },
    };

    const sectorConfig = {
        key: 'sector',
        getDataPointProps: data => {
            if (!data) return null;
            const sectors = get(data, 'properties.sector', []);
            if (!sectors.length) return null;
            const first = sectors[0];
            const primary = first.values.join(', ');
            const promotedContribution = toDrawerContribution(first, primary);
            const contributions = sectors
                .slice(1)
                .map(item =>
                    toDrawerContribution(item, item.values.join(', ')),
                );
            const drawerData = {
                promotedContribution,
                contributions,
            };
            return {
                label: FIELD_CONFIG.sector.label,
                value: primary,
                tooltipText: FIELD_CONFIG.sector.tooltipText,
                statusLabel: getStatusLabel(first.is_from_claim),
                contributorName: first.contributor_name || null,
                userId: first.contributor_id,
                date: first.created_at,
                drawerData,
            };
        },
    };

    const extendedConfigs = extendedTypes.map(({ fieldName, formatValue }) => ({
        key: fieldName,
        getDataPointProps: data => {
            if (!data) return null;
            let values = get(
                data,
                `properties.extended_fields.${fieldName}`,
                [],
            );
            const formatField = item =>
                formatExtendedField({ ...item, formatValue });
            if (fieldName === 'facility_type') {
                values = values.filter(extendedValue =>
                    extendedValue?.value?.matched_values?.some(
                        matchedValue => matchedValue[2],
                    ),
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
                            .filter(entry => {
                                if (!entry) return false;
                                if (Array.isArray(entry.primary))
                                    return entry.primary.length > 0;
                                return !!entry.primary;
                            });
                        if (!formattedEntries.length) return null;
                        const primary = formattedEntries.reduce(
                            (acc, value, index) => {
                                if (index > 0) acc.push('');
                                if (Array.isArray(value.primary))
                                    return acc.concat(value.primary);
                                acc.push(value.primary);
                                return acc;
                            },
                            [],
                        );
                        return {
                            ...formattedEntries[0],
                            primary,
                        };
                    })
                    .filter(Boolean);
                if (!formattedGroups.length) return null;
                const topGroup = formattedGroups[0];
                const valueDisplay = renderUniqueListItems(
                    topGroup.primary,
                    fieldName,
                );
                const topRaw = groupedContributions[0].items[0];
                const promotedContribution = toDrawerContribution(
                    topRaw,
                    valueDisplay,
                );
                const restGroups = formattedGroups.slice(1);
                const contributions = restGroups.flatMap(
                    (formattedGroup, groupIndex) => {
                        const group = groupedContributions[groupIndex + 1];
                        const groupValueDisplay = renderUniqueListItems(
                            formattedGroup.primary,
                            fieldName,
                        );
                        return (group?.items || []).map(contributionItem =>
                            toDrawerContribution(
                                contributionItem,
                                groupValueDisplay,
                            ),
                        );
                    },
                );
                return {
                    label: FIELD_CONFIG[fieldName].label,
                    value: valueDisplay,
                    tooltipText: FIELD_CONFIG[fieldName].tooltipText,
                    statusLabel: getStatusLabel(topGroup.isFromClaim),
                    contributorName: topRaw.contributor_name || null,
                    userId: topRaw.contributor_id,
                    date: topRaw.created_at,
                    drawerData: {
                        promotedContribution,
                        contributions,
                    },
                };
            }
            const topValue = formatField(values[0]);
            const promotedValueDisplay = renderUniqueListItems(
                topValue.primary,
                fieldName,
            );
            const promotedContribution = toDrawerContribution(
                values[0],
                promotedValueDisplay,
            );
            const contributions = values.slice(1).map(extendedItem => {
                const formatted = formatField(extendedItem);
                const valueDisplay = renderUniqueListItems(
                    formatted.primary,
                    fieldName,
                );
                return toDrawerContribution(extendedItem, valueDisplay);
            });
            return {
                label: FIELD_CONFIG[fieldName].label,
                value: topValue.primary,
                tooltipText: FIELD_CONFIG[fieldName].tooltipText,
                statusLabel: getStatusLabel(topValue.isFromClaim),
                contributorName: values[0].contributor_name || null,
                userId: values[0].contributor_id,
                date: values[0].created_at,
                drawerData: {
                    promotedContribution,
                    contributions,
                },
            };
        },
    }));

    const statusConfig = {
        key: 'status',
        getDataPointProps: data => {
            if (!data) return null;
            const items = formatActivityReports(data);
            if (!items.length) return null;
            const first = items[0];
            const promotedContribution = {
                value: first.primary,
                sourceName: first.sourceName || null,
                date: first.date || null,
                userId: undefined,
            };
            const contributions = items.slice(1).map(item => ({
                value: item.primary,
                sourceName: item.sourceName || null,
                date: item.date || null,
                userId: undefined,
            }));
            return {
                label: FIELD_CONFIG.status.label,
                value: first.primary,
                tooltipText: FIELD_CONFIG.status.tooltipText,
                statusLabel: STATUS_CROWDSOURCED,
                contributorName: first.sourceName || null,
                userId: null,
                date: first.date || null,
                drawerData: {
                    promotedContribution,
                    contributions,
                },
            };
        },
    };

    // Return the field configs in the order fields should be displayed.
    return [nameConfig, sectorConfig, ...extendedConfigs, statusConfig];
};

export const getSelectedDrawerItem = (items, fieldKey) =>
    fieldKey
        ? (items && items.find(item => item.key === fieldKey)) ?? null
        : null;

export const getVisibleFields = (data, includeAdditionalIdentifiers) => {
    if (!data) return [];
    const configs = getOrderedFieldConfigs(includeAdditionalIdentifiers);
    return configs
        .map(config => {
            const props = config.getDataPointProps(data);
            if (!props || props.value == null) return null;
            return { key: config.key, label: config.label, ...props };
        })
        .filter(Boolean);
};
