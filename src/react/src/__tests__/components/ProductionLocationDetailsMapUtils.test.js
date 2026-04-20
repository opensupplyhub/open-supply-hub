import {
    getContributorStatus,
    getFieldContributorInfo,
} from '../../components/ProductionLocation/ProductionLocationDetailsMap/utils';
import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
} from '../../components/ProductionLocation/DataPoint/constants';

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

    it('returns STATUS_CROWDSOURCED when contributorName is falsy but hasData is true', () => {
        expect(getContributorStatus('', false, true)).toBe(STATUS_CROWDSOURCED);
        expect(getContributorStatus(null, false, true)).toBe(STATUS_CROWDSOURCED);
    });

    it('returns STATUS_CLAIMED when contributorName is falsy but hasData is true and isFromClaim is true', () => {
        expect(getContributorStatus('', true, true)).toBe(STATUS_CLAIMED);
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

    it('uses created_from when only core properties.address is set (no extended_fields.address)', () => {
        const data = {
            properties: {
                address: '13736 Victory Blvd, Van Nuys, CA, 91401-2324',
                extended_fields: { address: [] },
                created_from: {
                    contributor: 'List / geocode source',
                    created_at: '2020-05-01T12:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.status).toBe(STATUS_CROWDSOURCED);
        expect(result.contributorName).toBe('List / geocode source');
        expect(result.date).toBe('2020-05-01T12:00:00Z');
        expect(result.drawerData.contributions).toEqual([]);
        expect(result.drawerData.promotedContribution.value).toBe(
            '13736 Victory Blvd, Van Nuys, CA, 91401-2324',
        );
        expect(result.drawerData.promotedContribution.sourceName).toBe(
            'List / geocode source',
        );
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

        expect(result.contributorName).toBe('');
        expect(result.userId).toBeNull();
        expect(result.date).toBe('');
        expect(result.status).toBe(STATUS_CROWDSOURCED);
        expect(result.drawerData.promotedContribution).not.toBeNull();
        expect(result.drawerData.promotedContribution.value).toBe('No Match');
        expect(result.drawerData.promotedContribution.sourceName).toBeNull();
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
        // doesn't match the entry's value ('123 Main St'), so fall back to
        // created_from (absent → empty). Promoted row uses core address as value.
        expect(result.drawerData.promotedContribution).not.toBeNull();
        expect(result.drawerData.promotedContribution.value).toBe('Other');
        expect(result.drawerData.promotedContribution.sourceName).toBeNull();
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

    it('does not list extra canonical rows in contributions (FacilityDetailsLocationFields parity)', () => {
        // Two contributors both report the canonical address. Legacy puts only
        // the first in the main line; the second is not in additionalContent
        // (same as primary === core partition). Drawer lists only otherFields.
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
        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe('Org C');
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

describe('getFieldContributorInfo — ADDRESS no-match fallback (legacy parity)', () => {
    it('falls back to created_from when extended rows exist but none match core address', () => {
        const data = {
            properties: {
                address: 'Core Address On Profile',
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2020-01-01T00:00:00Z',
                },
                extended_fields: {
                    address: [
                        {
                            value: 'Different St Only In Extended',
                            contributor_name: 'Submitter A',
                            contributor_id: 1,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                    ],
                },
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.contributorName).toBe('Origin Org');
        expect(result.date).toBe('2020-01-01T00:00:00Z');
        expect(result.status).toBe(STATUS_CROWDSOURCED);
        expect(result.drawerData.promotedContribution.value).toBe(
            'Core Address On Profile',
        );
        expect(result.drawerData.promotedContribution.sourceName).toBe(
            'Origin Org',
        );
        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe(
            'Submitter A',
        );
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

    it('does not treat a null-coordinate entry as canonical when facility also has null coordinates', () => {
        const data = {
            geometry: null,
            properties: {
                other_locations: [
                    {
                        lat: null,
                        lng: null,
                        contributor_name: 'Null Coord Org',
                        contributor_id: 1,
                        is_from_claim: false,
                    },
                ],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.contributorName).toBe('Origin Org');
        expect(result.drawerData.contributions).toHaveLength(0);
    });

    it('excludes null-coordinate entries from contributions even when has_invalid_location is absent', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [
                    {
                        lat: null,
                        lng: null,
                        contributor_name: 'Null Coord Org',
                        contributor_id: 1,
                        is_from_claim: false,
                    },
                    {
                        lat: 51.0,
                        lng: 0.0,
                        contributor_name: 'Valid Org',
                        contributor_id: 2,
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

        expect(result.drawerData.contributions).toHaveLength(1);
        expect(result.drawerData.contributions[0].sourceName).toBe('Valid Org');
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

describe('getFieldContributorInfo — getCorrespondingContributorId (userId fallback)', () => {
    it('resolves userId from properties.contributors when created_from contributor name matches — address case', () => {
        const data = {
            properties: {
                address: 'Core Address',
                extended_fields: { address: [] },
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2020-01-01T00:00:00Z',
                },
                contributors: [
                    { id: 42, contributor_name: 'Other Org' },
                    { id: 99, contributor_name: 'Origin Org' },
                ],
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.userId).toBe(99);
    });

    it('returns null userId when created_from contributor has no match in contributors list — address case', () => {
        const data = {
            properties: {
                address: 'Core Address',
                extended_fields: { address: [] },
                created_from: {
                    contributor: 'Unknown Org',
                    created_at: '2020-01-01T00:00:00Z',
                },
                contributors: [{ id: 42, contributor_name: 'Some Other Org' }],
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.userId).toBeNull();
    });

    it('returns null userId when properties.contributors is absent — address case', () => {
        const data = {
            properties: {
                address: 'Core Address',
                extended_fields: { address: [] },
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2020-01-01T00:00:00Z',
                },
                // no contributors array
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.userId).toBeNull();
    });

    it('uses canonicalRaw.contributor_id directly and does not fall through to contributors lookup — address case', () => {
        const data = {
            properties: {
                address: '123 Main St',
                extended_fields: {
                    address: [
                        {
                            value: '123 Main St',
                            contributor_name: 'Canonical Org',
                            contributor_id: 7,
                            created_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                    ],
                },
                contributors: [
                    // id differs from contributor_id in the extended field
                    { id: 99, contributor_name: 'Canonical Org' },
                ],
            },
        };

        const result = getFieldContributorInfo(data, ADDR);

        expect(result.userId).toBe(7);
    });

    it('resolves userId from properties.contributors in coordinates case when no canonical location', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                other_locations: [],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
                contributors: [{ id: 55, contributor_name: 'Origin Org' }],
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.userId).toBe(55);
    });

    it('uses canonicalLocation.contributor_id in coordinates case and does not fall through to contributors lookup', () => {
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
                ],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
                contributors: [
                    // id differs from the other_location entry's contributor_id
                    { id: 99, contributor_name: 'Origin Org' },
                ],
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.userId).toBe(10);
    });
});

describe('getFieldContributorInfo — COORDINATES coordinatesErrorText', () => {
    it('returns null when has_inexact_coordinates is false and no invalid-location entries exist', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                has_inexact_coordinates: false,
                other_locations: [
                    {
                        lat: 51.0,
                        lng: 0.0,
                        contributor_name: 'Some Org',
                        contributor_id: 1,
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

        expect(result.coordinatesErrorText).toBeNull();
    });

    it('returns the inexact-coordinates message when has_inexact_coordinates is true', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                has_inexact_coordinates: true,
                other_locations: [],
                created_from: {
                    contributor: 'Origin Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
            },
        };

        const result = getFieldContributorInfo(data, COORDS);

        expect(result.coordinatesErrorText).toContain(
            'Unable to locate exact GPS coordinates',
        );
    });

    it('returns the invalid-claim message when an other_location entry has has_invalid_location true', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                has_inexact_coordinates: false,
                other_locations: [
                    {
                        lat: null,
                        lng: null,
                        contributor_name: 'Claimant Org',
                        contributor_id: 1,
                        is_from_claim: true,
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

        expect(result.coordinatesErrorText).toContain(
            'The address provided by the claimant could not be geolocated',
        );
    });

    it('prioritises the inexact-coordinates message over the invalid-claim message when both conditions are true', () => {
        const data = {
            geometry: { coordinates: [-73.8, 40.7] },
            properties: {
                has_inexact_coordinates: true,
                other_locations: [
                    {
                        lat: null,
                        lng: null,
                        contributor_name: 'Claimant Org',
                        contributor_id: 1,
                        is_from_claim: true,
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

        expect(result.coordinatesErrorText).toContain(
            'Unable to locate exact GPS coordinates',
        );
        expect(result.coordinatesErrorText).not.toContain('claimant');
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
