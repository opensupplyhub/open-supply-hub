import get from 'lodash/get';
import head from 'lodash/head';
import partition from 'lodash/partition';
import uniqBy from 'lodash/uniqBy';

import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from '../DataPoint/constants';
import { FIELD_TYPE } from './constants';

export { FIELD_TYPE };

export const getContributorStatus = (contributorName, isFromClaim) => {
    if (!contributorName) return null;
    return isFromClaim ? STATUS_CLAIMED : STATUS_CROWDSOURCED;
};

/**
 * Returns contributor info (name, userId, date, status) and drawer data
 * (promotedContribution + contributions) for a given field type derived from
 * the singleFacilityData Redux object.
 *
 * @param {Object} singleFacilityData
 * @param {string} fieldType - one of FIELD_TYPE.*
 * @returns {{ contributorName: string, userId: number|string|null, date: string, status: string|null, drawerData: object }}
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

            // Same-contributor same-address
            // entries from different dates remain distinct.
            const uniqueAddressFields = uniqBy(
                addressFields,
                f =>
                    (get(f, 'value', '') || '') +
                    (get(f, 'created_at', '') || '') +
                    (get(f, 'contributor_name', '') || ''),
            );

            const [canonicalFields, otherFields] = partition(
                uniqueAddressFields,
                f => f.value === address,
            );
            // Do not fall back to an arbitrary entry when no field matches the
            // canonical address: that would attribute provenance to a
            // contributor who submitted a different address value entirely.
            const canonicalField = canonicalFields[0] || null;
            // When there is no canonical match, surface every known submission
            // in the drawer (no promoted contribution, all fields listed).
            const contributions = canonicalField
                ? [...canonicalFields.slice(1), ...otherFields]
                : uniqueAddressFields;

            const contributorName =
                get(canonicalField, 'contributor_name', '') || '';
            const userId = get(canonicalField, 'contributor_id', null);
            const date = get(canonicalField, 'created_at', '') || '';
            const status = getContributorStatus(
                contributorName,
                get(canonicalField, 'is_from_claim', false),
            );

            const promotedContribution = canonicalField
                ? {
                      value: get(canonicalField, 'value', '') || '',
                      sourceName: contributorName,
                      date:
                          get(canonicalField, 'created_at', '') ||
                          get(canonicalField, 'updated_at', '') ||
                          '',
                      userId,
                  }
                : null;

            const drawerData = {
                promotedContribution,
                contributions: contributions.map(field => ({
                    value: get(field, 'value', '') || '',
                    sourceName: get(field, 'contributor_name', '') || '',
                    date:
                        get(field, 'created_at', '') ||
                        get(field, 'updated_at', '') ||
                        '',
                    userId: get(field, 'contributor_id', null),
                })),
            };

            return { contributorName, userId, date, status, drawerData };
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
            // An entry is canonical only when its coordinates match the point
            // actually rendered on the map (geometry.coordinates). Using
            // is_from_claim alone as a canonical signal would attribute
            // provenance to a different coordinate when the claim's lat/lng
            // diverges from the displayed geometry (e.g. after an admin
            // location correction post-claim-approval).
            const [canonicalLocations, nonCanonicalLocations] = partition(
                otherLocations,
                ({ lng, lat, has_invalid_location: hasInvalidLocation }) =>
                    !hasInvalidLocation &&
                    lng === facilityLng &&
                    lat === facilityLat,
            );
            const canonicalLocation = head(canonicalLocations);

            // Prefer the contributor from the canonical other_location entry
            // (covers claims and admin location corrections). Fall back to
            // created_from.contributor for the common case where the primary
            // coordinates came directly from the original list-item geocoding.
            const locationContributorName =
                get(canonicalLocation, 'contributor_name', '') || '';
            const contributorName =
                locationContributorName ||
                get(
                    singleFacilityData,
                    'properties.created_from.contributor',
                    '',
                ) ||
                '';
            const userId = get(canonicalLocation, 'contributor_id', null);
            // other_locations items don't carry created_at. Only attach the
            // created_from date when the contributor itself also comes from
            // created_from; showing a date that belongs to a different
            // contributor would be misleading.
            const date = locationContributorName
                ? ''
                : get(
                      singleFacilityData,
                      'properties.created_from.created_at',
                      '',
                  ) || '';
            const status = getContributorStatus(
                contributorName,
                get(canonicalLocation, 'is_from_claim', false),
            );

            const primaryCoordValue =
                Array.isArray(coordinates) && coordinates.length >= 2
                    ? `${coordinates[1]}, ${coordinates[0]}`
                    : '';
            const promotedValue = canonicalLocation
                ? `${canonicalLocation.lat}, ${canonicalLocation.lng}`
                : primaryCoordValue;

            const promotedContribution = {
                value: promotedValue,
                sourceName: contributorName,
                date,
                userId,
            };

            // Include remaining canonical locations (slice(1)) so that
            // additional claims/corrections are not silently discarded.
            const contributions = [
                ...canonicalLocations
                    .slice(1)
                    .filter(item => !item.has_invalid_location),
                ...nonCanonicalLocations.filter(
                    item => !item.has_invalid_location,
                ),
            ].map(item => ({
                value: `${item.lat}, ${item.lng}`,
                sourceName: get(item, 'contributor_name', '') || '',
                date: '',
                userId: get(item, 'contributor_id', null),
            }));

            const drawerData = { promotedContribution, contributions };

            return { contributorName, userId, date, status, drawerData };
        }

        default:
            return {
                contributorName: '',
                userId: null,
                date: '',
                status: null,
                drawerData: { promotedContribution: null, contributions: [] },
            };
    }
};
