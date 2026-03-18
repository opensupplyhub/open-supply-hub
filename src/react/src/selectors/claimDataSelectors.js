import { createSelector } from '@reduxjs/toolkit';
import filter from 'lodash/filter';
import get from 'lodash/get';
import isString from 'lodash/isString';
import isEmpty from 'lodash/isEmpty';

import {
    getLocationFieldsConfig,
    hasDisplayableValue,
} from '../components/FacilityDetailsClaimedInfo/utils';
import sortClaimFields from '../components/ProductionLocation/ClaimSection/ClaimDataContainer/utils';
import { facilityClaimStatusChoicesEnum } from '../util/constants';

export const getClaimInfo = state =>
    get(state, 'facilities.singleFacility.data.properties.claim_info', null);

export const getIsClaimed = createSelector(getClaimInfo, claimInfo => {
    if (!claimInfo) return false;
    return claimInfo.status !== facilityClaimStatusChoicesEnum.PENDING;
});

const EMPTY_CLAIM_DATA = Object.freeze({
    displayableFields: [],
    contributorName: null,
    contributorUserId: null,
    claimedAt: null,
});

export const getClaimDisplayData = createSelector(
    getClaimInfo,
    getIsClaimed,
    (claimInfo, isClaimed) => {
        if (!isClaimed || !claimInfo) {
            return EMPTY_CLAIM_DATA;
        }

        const { facility, contact, office } = claimInfo;

        const contributorName = isString(claimInfo.contributor)
            ? claimInfo.contributor
            : get(claimInfo, 'contributor.name', null);

        const contributorUserId = get(claimInfo, 'user_id', null);

        const claimedAt =
            get(claimInfo, 'approved_at') ||
            get(claimInfo, 'created_at') ||
            null;

        const fieldsConfig = getLocationFieldsConfig(
            facility || {},
            contact || null,
            office || null,
        );

        const displayableFields = sortClaimFields(
            filter(fieldsConfig, field =>
                hasDisplayableValue(field.getValue()),
            ),
        );

        return {
            hasDisplayableFields: !isEmpty(displayableFields),
            displayableFields,
            contributorName,
            contributorUserId,
            claimedAt,
        };
    },
);
