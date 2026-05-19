import { createSelector } from '@reduxjs/toolkit';
import get from 'lodash/get';
import { preparePartnerFields } from '../components/PartnerFields/PartnerFieldsSection/utils.jsx';

const EMPTY_GROUPS = [];

const getGroups = state =>
    state.partnerFieldGroups.data?.results || EMPTY_GROUPS;

const getFacilityData = state => state.facilities.singleFacility.data;

export const getEnrichedPartnerGroups = createSelector(
    [getFacilityData, getGroups],
    (facilityData, groups) => {
        const partnerFields = preparePartnerFields(facilityData) ?? [];
        return groups.map(group => ({
            ...group,
            partnerFields: partnerFields.filter(field =>
                group.partner_fields.includes(field.fieldName),
            ),
        }));
    },
);

export const getVisiblePartnerGroups = createSelector(
    [getEnrichedPartnerGroups, getFacilityData],
    (enrichedGroups, facilityData) =>
        enrichedGroups.filter(group =>
            group.partnerFields?.some(field => {
                const values = get(
                    facilityData,
                    `properties.partner_fields.${field.fieldName}`,
                    [],
                );
                return values.length > 0 && !!values[0];
            }),
        ),
);

/**
 * Formats partner group contributors data into the shape expected by
 * NestedSelect / DataPartnersFilter:
 * [{ label: groupLabel, options: [{ groupLabel, label, value: String(id) }] }]
 */
const EMPTY_CONTRIBUTOR_GROUPS = [];

const getContributorGroups = state =>
    state.partnerGroupContributors.data?.results || EMPTY_CONTRIBUTOR_GROUPS;

export const getPartnerGroupsWithContributors = createSelector(
    [getContributorGroups],
    groups =>
        groups.map(group => ({
            label: group.label,
            options: (group.contributors || []).map(c => ({
                groupLabel: group.label,
                label: c.name,
                value: String(c.id),
            })),
        })),
);
