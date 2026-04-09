import get from 'lodash/get';
import head from 'lodash/head';
import find from 'lodash/find';
import partition from 'lodash/partition';
import trim from 'lodash/trim';
import uniqBy from 'lodash/uniqBy';

import { formatExtendedField } from '../../../util/util';

import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from '../DataPoint/constants';
import { FIELD_CONFIG } from '../constants';

export const getContributorStatus = (
    contributorName,
    isFromClaim,
    hasData = false,
) => {
    if (!contributorName && !hasData) return null;
    return isFromClaim ? STATUS_CLAIMED : STATUS_CROWDSOURCED;
};

const toDrawerContribution = (item, value) => ({
    value,
    sourceName: item.contributor_name || null,
    date: item.created_at || item.updated_at || null,
    userId: item.contributor_id != null ? item.contributor_id : undefined,
});

// We don't have contributor id in properties.created_from,
// so we try to find corresponding id from properties.contributors list.
const getCorrespondingContributorId = data => {
    const contributorsList = get(data, 'properties.contributors');
    const correspondingContributor = find(
        contributorsList,
        contributor =>
            contributor.contributor_name ===
            get(data, 'properties.created_from.contributor'),
    );

    return get(correspondingContributor, 'id', null);
};

/**
 * @param {Object} singleFacilityData
 * @param {string} fieldType
 * @returns {{
 * contributorName: string,
 * userId: number|string|null,
 * date: string,
 * status: string|null,
 * drawerData: object
 * }}
 */
export const getFieldContributorInfo = (singleFacilityData, fieldType) => {
    switch (fieldType) {
        case FIELD_CONFIG.address.key: {
            const address =
                get(singleFacilityData, 'properties.address', '') || '';
            const addressFields = get(
                singleFacilityData,
                'properties.extended_fields.address',
                [],
            );

            const uniqueAddresses = uniqBy(
                addressFields.map(formatExtendedField),
                item => item.primary + item.secondary,
            );

            const [canonicalFormattedList, otherFormatted] = partition(
                uniqueAddresses,
                field => field.primary === address,
            );
            const canonicalFormatted = canonicalFormattedList[0] || null;
            const contributionsFormatted = canonicalFormatted
                ? otherFormatted
                : uniqueAddresses;

            const findRawForFormatted = formatted =>
                addressFields.find(raw => {
                    const f = formatExtendedField(raw);
                    return (
                        f.primary === formatted.primary &&
                        f.secondary === formatted.secondary
                    );
                });

            const canonicalRaw = canonicalFormatted
                ? addressFields.find(
                      raw =>
                          formatExtendedField(raw).primary ===
                          canonicalFormatted.primary,
                  )
                : null;

            const userId = get(
                canonicalRaw,
                'contributor_id',
                getCorrespondingContributorId(singleFacilityData),
            );
            const hasExtendedAddressData = uniqueAddresses.length > 0;

            // Fall back to created_from whenever no extended row matches the core address
            // (mirrors legacy FacilityDetailsLocationFields behaviour: use created_from
            // when !defaultAddressField.length && !!coreAddress).
            const useCreatedFrom = !canonicalRaw && trim(address);
            const attributionSource =
                canonicalRaw ||
                (useCreatedFrom
                    ? {
                          contributor_name: get(
                              singleFacilityData,
                              'properties.created_from.contributor',
                              '',
                          ),
                          created_at: get(
                              singleFacilityData,
                              'properties.created_from.created_at',
                              '',
                          ),
                          is_from_claim: false,
                      }
                    : null);

            const contributorName =
                get(attributionSource, 'contributor_name', '') || '';
            const date = attributionSource
                ? get(attributionSource, 'created_at', '') ||
                  get(attributionSource, 'updated_at', '') ||
                  ''
                : '';

            const hasDataForStatusBadge =
                hasExtendedAddressData || Boolean(trim(address));
            const status = getContributorStatus(
                contributorName,
                get(attributionSource, 'is_from_claim', false),
                hasDataForStatusBadge,
            );

            const promotedValue = canonicalRaw
                ? canonicalFormatted.primary
                : address;

            const countryName =
                get(singleFacilityData, 'properties.country_name', '') || '';
            const displayValue =
                trim(promotedValue) && trim(countryName)
                    ? `${promotedValue} - ${countryName}`
                    : promotedValue;

            const promotedContribution = attributionSource
                ? toDrawerContribution(attributionSource, displayValue)
                : null;

            const drawerData = {
                promotedContribution,
                contributions: contributionsFormatted.map(formatted =>
                    toDrawerContribution(
                        findRawForFormatted(formatted) || {},
                        formatted.primary,
                    ),
                ),
            };

            return {
                key: 'address',
                label: FIELD_CONFIG.address.label,
                tooltipText: FIELD_CONFIG.address.tooltipText,
                displayValue,
                contributorName,
                userId,
                date,
                status,
                drawerData,
            };
        }

        case FIELD_CONFIG.coordinates.key: {
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
            const COORD_EPSILON = 1e-10;
            const [canonicalLocations, nonCanonicalLocations] = partition(
                otherLocations,
                ({ lng, lat, has_invalid_location: hasInvalidLocation }) =>
                    facilityLat != null &&
                    facilityLng != null &&
                    lat != null &&
                    lng != null &&
                    !hasInvalidLocation &&
                    Math.abs(lng - facilityLng) < COORD_EPSILON &&
                    Math.abs(lat - facilityLat) < COORD_EPSILON,
            );
            const canonicalLocation = head(canonicalLocations);

            const hasInexactCoordinates =
                singleFacilityData?.properties?.has_inexact_coordinates;

            const hasInvalidClaimCoordinates = otherLocations.some(
                item => item.has_invalid_location,
            );

            // If the coordinates error text is not empty, it will be shown
            // instead of contributor name (this logic implemented in the DataPoint component).
            const coordinatesErrorText = () => {
                if (hasInexactCoordinates) {
                    return `Unable to locate exact GPS coordinates for this production location. If you
                        have access to accurate address for this production location, please report it using the "Suggest Correction" link.`;
                }
                if (hasInvalidClaimCoordinates) {
                    return "The address provided by the claimant could not be geolocated. An alternate address' GPS is displayed.";
                }
                return null;
            };

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
            const userId = get(
                canonicalLocation,
                'contributor_id',
                getCorrespondingContributorId(singleFacilityData),
            );
            const date = '';
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

            const promotedContribution = canonicalLocation
                ? toDrawerContribution(canonicalLocation, promotedValue)
                : toDrawerContribution(
                      { contributor_name: contributorName },
                      promotedValue,
                  );

            // Include remaining canonical locations (slice(1)) so that
            // additional claims/corrections are not silently discarded.
            const hasValidCoords = item => item.lat != null && item.lng != null;
            const contributions = [
                ...canonicalLocations
                    .slice(1)
                    .filter(
                        item =>
                            !item.has_invalid_location && hasValidCoords(item),
                    ),
                ...nonCanonicalLocations.filter(
                    item => !item.has_invalid_location && hasValidCoords(item),
                ),
            ].map(item =>
                toDrawerContribution(item, `${item.lat}, ${item.lng}`),
            );

            const drawerData = { promotedContribution, contributions };

            return {
                key: 'coordinates',
                label: FIELD_CONFIG.coordinates.label,
                tooltipText: FIELD_CONFIG.coordinates.tooltipText,
                contributorName,
                coordinatesErrorText: coordinatesErrorText(),
                userId,
                date,
                status,
                drawerData,
            };
        }

        default:
            return {
                key: null,
                label: null,
                tooltipText: null,
                contributorName: '',
                userId: null,
                date: '',
                status: null,
                drawerData: { promotedContribution: null, contributions: [] },
            };
    }
};
