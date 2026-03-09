import get from 'lodash/get';
import head from 'lodash/head';
import partition from 'lodash/partition';

import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from '../DataPoint/constants';
import { FIELD_TYPE } from './constants';

export { FIELD_TYPE };

export const getContributorStatus = (contributorName, isFromClaim) => {
    if (!contributorName) return null;
    return isFromClaim ? STATUS_CLAIMED : STATUS_CROWDSOURCED;
};

/**
 * Returns the contributor info (name, userId, date, status) for a given
 * field type derived from the singleFacilityData Redux object.
 *
 * @param {Object} singleFacilityData
 * @param {string} fieldType - one of FIELD_TYPE.*
 * @returns {{ contributorName: string, userId: number|string|null, date: string, status: string|null }}
 */
export const getFieldContributorInfo = (singleFacilityData, fieldType) => {
    switch (fieldType) {
        case FIELD_TYPE.ADDRESS: {
            const address =
                get(singleFacilityData, 'properties.address', '') || '';
            const addressFields = get(
                singleFacilityData,
                'properties.extended_fields.address',
                [],
            );
            const canonicalField =
                addressFields.find(f => f.value === address) ||
                addressFields[0];

            const contributorName =
                get(canonicalField, 'contributor_name', '') || '';
            const userId = get(canonicalField, 'contributor_id', null);
            const date = get(canonicalField, 'created_at', '') || '';
            const status = getContributorStatus(
                contributorName,
                get(canonicalField, 'is_from_claim', false),
            );

            return { contributorName, userId, date, status };
        }

        case FIELD_TYPE.COORDINATES: {
            const coordinates = get(
                singleFacilityData,
                'geometry.coordinates',
                null,
            );
            const facilityLng = Array.isArray(coordinates)
                ? coordinates[0]
                : null;
            const facilityLat = Array.isArray(coordinates)
                ? coordinates[1]
                : null;
            const otherLocations = get(
                singleFacilityData,
                'properties.other_locations',
                [],
            );
            const [canonicalLocations] = partition(
                otherLocations,
                ({
                    lng,
                    lat,
                    is_from_claim: isFromClaim,
                    has_invalid_location: hasInvalidLocation,
                }) =>
                    (isFromClaim && !hasInvalidLocation) ||
                    (lng === facilityLng && lat === facilityLat),
            );
            const canonicalLocation = head(canonicalLocations);

            // Prefer the contributor from the canonical other_location entry
            // (covers claims and admin location corrections). Fall back to
            // created_from.contributor for the common case where the primary
            // coordinates came directly from the original list-item geocoding.
            const contributorName =
                get(canonicalLocation, 'contributor_name', '') ||
                get(
                    singleFacilityData,
                    'properties.created_from.contributor',
                    '',
                ) ||
                '';
            const userId = get(canonicalLocation, 'contributor_id', null);
            // other_locations items don't carry created_at; fall back to the
            // facility's origin-contribution date as the best available approximation.
            const date =
                get(
                    singleFacilityData,
                    'properties.created_from.created_at',
                    '',
                ) || '';
            const status = getContributorStatus(
                contributorName,
                get(canonicalLocation, 'is_from_claim', false),
            );

            return { contributorName, userId, date, status };
        }

        default:
            return {
                contributorName: '',
                userId: null,
                date: '',
                status: null,
            };
    }
};
