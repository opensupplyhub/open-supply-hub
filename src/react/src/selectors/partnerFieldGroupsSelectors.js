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
                group.partner_fields.some(pf => pf.name === field.fieldName),
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
 * Formats partner field groups data into a shape suitable for the
 * SpotlightDataPartnersFilter component:
 * [{ value: uuid, label: name, partnerFields: [{ value: name, label }] }]
 */
export const getPartnerGroupsForFilter = createSelector([getGroups], groups =>
    groups.map(group => ({
        value: group.uuid,
        label: group.name,
        partnerFields: (group.partner_fields || []).map(pf => ({
            value: pf.name,
            label: pf.label || pf.name,
        })),
    })),
);
