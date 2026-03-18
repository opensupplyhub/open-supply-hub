import { createSelector } from '@reduxjs/toolkit';
import get from 'lodash/get';
import { preparePartnerFields } from '../components/PartnerFields/PartnerFieldsSection/utils.jsx';

const getGroups = state => state.partnerFieldGroups.data?.results || [];

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
