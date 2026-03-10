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

// ---------------------------------------------------------------------------
// getContributorStatus
// ---------------------------------------------------------------------------
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

// ---------------------------------------------------------------------------
// getFieldContributorInfo — ADDRESS
// ---------------------------------------------------------------------------
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

    it('falls back to the first entry when no field matches properties.address', () => {
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

        expect(result.contributorName).toBe('First Org');
        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe('Second Org');
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

        // 3 identical raw entries → deduped to 1; that 1 becomes the canonical
        // (first) with no remaining contributions.
        expect(result.drawerData.contributions).toHaveLength(0);
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
        expect(result.date).toBe('2023-01-01T00:00:00Z');
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

    it('identifies canonical location by is_from_claim when not invalid', () => {
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

        expect(result.contributorName).toBe('Claimed Org');
        expect(result.status).toBe(STATUS_CLAIMED);
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

    it('includes extra canonical locations in contributions', () => {
        // Two is_from_claim entries: first becomes the promoted location,
        // second must appear in contributions rather than being dropped.
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: 51.0,
                        lng: 0.0,
                        contributor_name: 'Claim A',
                        contributor_id: 10,
                        is_from_claim: true,
                        has_invalid_location: false,
                    },
                    {
                        lat: 52.0,
                        lng: 1.0,
                        contributor_name: 'Claim B',
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

        expect(result.contributorName).toBe('Claim A');
        // Claim B (second canonical) + Non-claim Org = 2 contributions
        expect(result.drawerData.contributions).toHaveLength(2);
        expect(
            result.drawerData.contributions.map(c => c.sourceName),
        ).toEqual(['Claim B', 'Non-claim Org']);
    });

    it('uses created_from date only when contributor also comes from created_from', () => {
        // No matching other_location → both contributor and date come from
        // created_from, so provenance is consistent.
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
        expect(result.date).toBe('2023-01-01T00:00:00Z');
        expect(result.drawerData.promotedContribution.date).toBe(
            '2023-01-01T00:00:00Z',
        );
    });

    it('suppresses created_from date when canonical location provides the contributor', () => {
        // other_locations carries contributor_name but no created_at.
        // Showing created_from.created_at here would be misleading because
        // it belongs to a different contributor.
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: 51.0,
                        lng: 0.0,
                        contributor_name: 'Claimed Org',
                        contributor_id: 99,
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
        expect(result.date).toBe('');
        expect(result.drawerData.promotedContribution.date).toBe('');
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
