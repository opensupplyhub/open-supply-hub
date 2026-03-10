import {
    getContributorStatus,
    getFieldContributorInfo,
} from '../../components/ProductionLocation/ProductionLocationDetailsMap/utils';
import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
} from '../../components/ProductionLocation/DataPoint/constants';

// constants.js (imported transitively by utils.js) calls L.icon at module
// initialisation time. jest.mock is hoisted before imports at runtime, so the
// order here is only for the linter.
jest.mock('leaflet', () => ({ icon: jest.fn(() => ({})) }));

const ADDR = 'address';
const COORDS = 'coordinates';

describe('getContributorStatus', () => {
    it('returns null when contributorName is falsy', () => {
        expect(getContributorStatus('', false)).toBeNull();
        expect(getContributorStatus(null, false)).toBeNull();
        expect(getContributorStatus(undefined, true)).toBeNull();
    });

    it('returns STATUS_CLAIMED when isFromClaim is true', () => {
        expect(getContributorStatus('Test Org', true)).toBe(STATUS_CLAIMED);
    });

    it('returns STATUS_CROWDSOURCED when isFromClaim is false', () => {
        expect(getContributorStatus('Test Org', false)).toBe(STATUS_CROWDSOURCED);
    });
});

describe('getFieldContributorInfo — ADDRESS', () => {
    it('returns empty defaults when singleFacilityData is null', () => {
        const result = getFieldContributorInfo(null, ADDR);

        expect(result.contributorName).toBe('');
        expect(result.userId).toBeNull();
        expect(result.date).toBe('');
        expect(result.status).toBeNull();
        expect(result.drawerData.promotedContribution).toBeNull();
        expect(result.drawerData.contributions).toEqual([]);
    });

    it('uses the field matching properties.address as the canonical contributor', () => {
        const data = {
            properties: {
                address: '123 Main St',
                extended_fields: {
                    address: [
                        {
                            value: '123 Main St',
                            contributor_name: 'Canonical Org',
                            contributor_id: 1,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                        {
                            value: '456 Other St',
                            contributor_name: 'Other Org',
                            contributor_id: 2,
                            created_at: '2023-02-01T00:00:00Z',
                            updated_at: '2023-02-01T00:00:00Z',
                            is_from_claim: false,
                        },
                    ],
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.contributorName).toBe('Canonical Org');
        expect(result.userId).toBe(1);
        expect(result.drawerData.promotedContribution.value).toBe('123 Main St');
        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe('Other Org');
    });

    it('shows no attribution and surfaces all fields when no entry matches properties.address', () => {
        // No extended_field value matches properties.address. Promoting
        // uniqueAddressFields[0] arbitrarily would attribute the displayed
        // address to a contributor who submitted a different value. Instead,
        // canonicalField is null and all submissions appear in contributions.
        const data = {
            properties: {
                address: 'No Match',
                extended_fields: {
                    address: [
                        {
                            value: 'First St',
                            contributor_name: 'First Org',
                            contributor_id: 1,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                        {
                            value: 'Second St',
                            contributor_name: 'Second Org',
                            contributor_id: 2,
                            created_at: '2023-02-01T00:00:00Z',
                            updated_at: '2023-02-01T00:00:00Z',
                            is_from_claim: false,
                        },
                    ],
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        // No canonical match → no attribution on the displayed address row.
        expect(result.contributorName).toBe('');
        expect(result.userId).toBeNull();
        expect(result.date).toBe('');
        expect(result.status).toBeNull();
        expect(result.drawerData.promotedContribution).toBeNull();
        // All extended_fields appear in the drawer.
        expect(result.drawerData.contributions).toHaveLength(2);
        expect(
            result.drawerData.contributions.map(c => c.sourceName),
        ).toEqual(['First Org', 'Second Org']);
    });

    it('deduplicates entries with identical value + created_at + contributor_name', () => {
        const entry = {
            value: '123 Main St',
            contributor_name: 'Test Org',
            contributor_id: 1,
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z',
            is_from_claim: false,
        };
        const data = {
            properties: {
                address: 'Other',
                extended_fields: {
                    address: [entry, { ...entry }, entry],
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        // 3 identical raw entries → deduped to 1. properties.address ('Other')
        // doesn't match the entry's value ('123 Main St'), so no canonical
        // field is promoted. The 1 deduplicated entry appears in contributions.
        expect(result.drawerData.promotedContribution).toBeNull();
        expect(result.drawerData.contributions).toHaveLength(1);
    });

    it('keeps entries separate when value+contributor match but created_at differs', () => {
        // entry1  → canonical (matches properties.address)
        // entry2  → contribution: 'Other St', 'Other Org', date A
        // entry3  → contribution: 'Other St', 'Other Org', same value+org, date B
        //
        // Without created_at in the dedup key entry2 and entry3 collapse to one
        // contribution. With it they remain distinct, giving length 2.
        const data = {
            properties: {
                address: '123 Main St',
                extended_fields: {
                    address: [
                        {
                            value: '123 Main St',
                            contributor_name: 'Canonical Org',
                            contributor_id: 1,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                        {
                            value: 'Other St',
                            contributor_name: 'Other Org',
                            contributor_id: 2,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                        {
                            value: 'Other St',
                            contributor_name: 'Other Org',
                            contributor_id: 2,
                            created_at: '2023-06-01T00:00:00Z',
                            updated_at: '2023-06-01T00:00:00Z',
                            is_from_claim: false,
                        },
                    ],
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.drawerData.contributions).toHaveLength(2);
    });

    it('includes extra canonical entries (same address) in contributions', () => {
        // Two different contributors both report the canonical address.
        // Only the first becomes the promoted entry; the second must appear
        // in contributions rather than being silently discarded.
        const data = {
            properties: {
                address: '123 Main St',
                extended_fields: {
                    address: [
                        {
                            value: '123 Main St',
                            contributor_name: 'Org A',
                            contributor_id: 1,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                        {
                            value: '123 Main St',
                            contributor_name: 'Org B',
                            contributor_id: 2,
                            created_at: '2023-02-01T00:00:00Z',
                            updated_at: '2023-02-01T00:00:00Z',
                            is_from_claim: false,
                        },
                        {
                            value: 'Other St',
                            contributor_name: 'Org C',
                            contributor_id: 3,
                            created_at: '2023-03-01T00:00:00Z',
                            updated_at: '2023-03-01T00:00:00Z',
                            is_from_claim: false,
                        },
                    ],
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.contributorName).toBe('Org A');
        // Org B (second canonical) + Org C (non-canonical) = 2 contributions
        expect(result.drawerData.contributions).toHaveLength(2);
        expect(
            result.drawerData.contributions.map(c => c.sourceName),
        ).toEqual(['Org B', 'Org C']);
    });

    it('sets STATUS_CLAIMED when the canonical field is_from_claim is true', () => {
        const data = {
            properties: {
                address: '123 Main St',
                extended_fields: {
                    address: [
                        {
                            value: '123 Main St',
                            contributor_name: 'Claimed Org',
                            contributor_id: 1,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: true,
                        },
                    ],
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.status).toBe(STATUS_CLAIMED);
    });
});

describe('getFieldContributorInfo — COORDINATES', () => {
    it('returns empty defaults when singleFacilityData is null', () => {
        const result = getFieldContributorInfo(null, COORDS);

        expect(result.contributorName).toBe('');
        expect(result.userId).toBeNull();
        expect(result.date).toBe('');
        expect(result.status).toBeNull();
        expect(result.drawerData.contributions).toEqual([]);
    });

    it('falls back to created_from.contributor when no canonical other_location', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.contributorName).toBe('Origin Org');
    });

    it('identifies canonical location by matching lat/lng', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: 40.7,
                        lng: -73.8,
                        contributor_name: 'Canonical Org',
                        contributor_id: 10,
                        is_from_claim: false,
                        has_invalid_location: false,
                    },
                    {
                        lat: 51.0,
                        lng: 0.0,
                        contributor_name: 'Other Org',
                        contributor_id: 20,
                        is_from_claim: false,
                        has_invalid_location: false,
                    },
                ],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.contributorName).toBe('Canonical Org');
        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe('Other Org');
    });

    it('identifies a claim as canonical when its coordinates match the geometry', () => {
        // Claim whose lat/lng match geometry.coordinates → canonical.
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: 40.7,
                        lng: -73.8,
                        contributor_name: 'Claimed Org',
                        contributor_id: 10,
                        is_from_claim: true,
                        has_invalid_location: false,
                    },
                ],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.contributorName).toBe('Claimed Org');
        expect(result.status).toBe(STATUS_CLAIMED);
    });

    it('does not treat a claim as canonical when its coordinates differ from the geometry', () => {
        // Claim lat/lng differ from geometry.coordinates (e.g. after an admin
        // location correction post-claim-approval). The claim must fall to
        // contributions and provenance falls back to created_from.
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: 51.0,
                        lng: 0.0,
                        contributor_name: 'Claimed Org',
                        contributor_id: 10,
                        is_from_claim: true,
                        has_invalid_location: false,
                    },
                ],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        // Claim is not canonical → fall back to created_from attribution.
        expect(result.contributorName).toBe('Origin Org');
        // The mismatched claim still appears as a contribution.
        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe(
            'Claimed Org',
        );
    });

    it('filters has_invalid_location entries from contributions', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: 51.0,
                        lng: 0.0,
                        contributor_name: 'Valid Org',
                        contributor_id: 1,
                        is_from_claim: false,
                        has_invalid_location: false,
                    },
                    {
                        lat: 90.0,
                        lng: 0.0,
                        contributor_name: 'Invalid Org',
                        contributor_id: 2,
                        is_from_claim: false,
                        has_invalid_location: true,
                    },
                ],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe('Valid Org');
    });

    it('includes non-matching other_locations in contributions', () => {
        // One entry matches geometry.coordinates → canonical.
        // The remaining entries (claim and non-claim with different lat/lng)
        // must appear in contributions rather than being dropped.
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: 40.7,
                        lng: -73.8,
                        contributor_name: 'Matching Org',
                        contributor_id: 10,
                        is_from_claim: true,
                        has_invalid_location: false,
                    },
                    {
                        lat: 52.0,
                        lng: 1.0,
                        contributor_name: 'Other Claim',
                        contributor_id: 20,
                        is_from_claim: true,
                        has_invalid_location: false,
                    },
                    {
                        lat: 53.0,
                        lng: 2.0,
                        contributor_name: 'Non-claim Org',
                        contributor_id: 30,
                        is_from_claim: false,
                        has_invalid_location: false,
                    },
                ],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.contributorName).toBe('Matching Org');
        // Other Claim + Non-claim Org = 2 contributions
        expect(result.drawerData.contributions).toHaveLength(2);
        expect(
            result.drawerData.contributions.map(c => c.sourceName),
        ).toEqual(['Other Claim', 'Non-claim Org']);
    });

    it('formats the promoted coordinate value as "lat, lng"', () => {
        const data = {
            geometry: { coordinates: [-73.8314318, 40.762569] },
            properties: {
                other_locations: [],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.drawerData.promotedContribution.value).toBe(
            '40.762569, -73.8314318',
        );
    });
});

describe('getFieldContributorInfo — default', () => {
    it('returns empty defaults for an unknown field type', () => {
        const result = getFieldContributorInfo({}, 'unknown_type');

        expect(result.contributorName).toBe('');
        expect(result.userId).toBeNull();
        expect(result.date).toBe('');
        expect(result.status).toBeNull();
        expect(result.drawerData.promotedContribution).toBeNull();
        expect(result.drawerData.contributions).toEqual([]);
    });
});
