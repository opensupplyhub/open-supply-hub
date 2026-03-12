import getVisibleFields from '../components/ProductionLocation/ProductionLocationDetailsGeneralFields/utils';

/**
 * Anonymized facility data for getVisibleFields tests.
 * Structure preserves behavior; all identifiable data replaced with placeholders.
 */
const anonymizedFacilityData = {
    id: 'XX0000000000000',
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: [0, 0],
    },
    properties: {
        name: 'Facility A',
        address: 'Address Line One',
        country_code: 'XX',
        os_id: 'XX0000000000000',
        other_names: ['FACILITY A', 'Facility A Ltd'],
        other_addresses: ['Address Line One', 'Address Line Two'],
        contributors: [
            {
                id: 1,
                name: 'Contributor A (List A)',
                is_verified: false,
                contributor_name: 'Contributor A',
                list_name: 'List A',
            },
        ],
        country_name: 'Country X',
        claim_info: null,
        other_locations: [],
        is_closed: true,
        activity_reports: [
            {
                facility: 'XX0000000000000',
                reported_by_contributor: 'Source A',
                closure_state: 'CLOSED',
                approved_at: '2020-01-01T00:00:00.000Z',
                status_change_reason: 'Closure reason',
                status: 'CONFIRMED',
                status_change_by: 'Source A',
                status_change_date: '2020-01-01T00:00:00.000Z',
                created_at: '2020-01-01T00:00:00.000Z',
                updated_at: '2020-01-01T00:00:00.000Z',
                id: 1,
                reason_for_report: 'Report reason',
                facility_name: 'Facility A',
            },
        ],
        contributor_fields: [],
        new_os_id: null,
        has_inexact_coordinates: false,
        extended_fields: {
            name: [
                {
                    value: 'Facility A',
                    field_name: 'name',
                    contributor_id: 1,
                    contributor_name: 'Contributor A',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    created_at: '2020-01-01T00:00:00.000Z',
                },
            ],
            address: [
                {
                    value: 'Address Line One',
                    field_name: 'address',
                    contributor_id: 1,
                    contributor_name: 'Contributor A',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    is_from_claim: false,
                    created_at: '2020-01-01T00:00:00.000Z',
                },
            ],
            number_of_workers: [
                {
                    id: 1,
                    is_verified: false,
                    value: { max: 500, min: 500 },
                    created_at: '2020-01-01T00:00:00.000Z',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    contributor_name: 'Contributor A',
                    contributor_id: 1,
                    value_count: 1,
                    is_from_claim: false,
                    field_name: 'number_of_workers',
                },
            ],
            native_language_name: [],
            facility_type: [
                {
                    id: 1,
                    is_verified: false,
                    value: {
                        raw_values: 'Type A',
                        matched_values: [
                            [
                                'FACILITY_TYPE',
                                'EXACT',
                                'Type A',
                                'Type A',
                            ],
                        ],
                    },
                    created_at: '2020-01-01T00:00:00.000Z',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    contributor_name: 'Contributor A',
                    contributor_id: 1,
                    value_count: 1,
                    is_from_claim: false,
                    field_name: 'facility_type',
                },
            ],
            processing_type: [
                {
                    id: 1,
                    is_verified: false,
                    value: {
                        raw_values: 'Type B',
                        matched_values: [
                            [
                                'PROCESSING_TYPE',
                                'EXACT',
                                'Type B',
                                'Type B',
                            ],
                        ],
                    },
                    created_at: '2020-01-01T00:00:00.000Z',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    contributor_name: 'Contributor A',
                    contributor_id: 1,
                    value_count: 1,
                    is_from_claim: false,
                    field_name: 'processing_type',
                },
            ],
            product_type: [
                {
                    id: 1,
                    is_verified: false,
                    value: { raw_values: ['Product A'] },
                    created_at: '2020-01-01T00:00:00.000Z',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    contributor_name: 'Contributor A',
                    contributor_id: 1,
                    value_count: 1,
                    is_from_claim: false,
                    field_name: 'product_type',
                },
            ],
            parent_company: [
                {
                    id: 1,
                    is_verified: false,
                    value: {
                        name: 'Parent A',
                        raw_value: 'Parent A',
                    },
                    created_at: '2020-01-01T00:00:00.000Z',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    contributor_name: 'Contributor A',
                    contributor_id: 1,
                    value_count: 1,
                    is_from_claim: false,
                    field_name: 'parent_company',
                },
            ],
            parent_company_os_id: [],
            duns_id: [],
            lei_id: [],
            rba_id: [
                {
                    id: 1,
                    is_verified: false,
                    value: { raw_value: 'RBA-001' },
                    created_at: '2020-01-01T00:00:00.000Z',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    contributor_name: 'Contributor A',
                    contributor_id: 1,
                    value_count: 1,
                    is_from_claim: false,
                    field_name: 'rba_id',
                },
            ],
            isic_4: [
                {
                    id: 1,
                    is_verified: false,
                    value: {
                        raw_value: [
                            {
                                class: '2620 - Class A',
                                group: '262 - Group A',
                                section: 'C - Manufacturing',
                                division: '26 - Division A',
                            },
                        ],
                    },
                    created_at: '2020-01-01T00:00:00.000Z',
                    updated_at: '2020-01-01T00:00:00.000Z',
                    contributor_name: 'Contributor A',
                    contributor_id: 1,
                    value_count: 1,
                    is_from_claim: false,
                    field_name: 'isic_4',
                },
            ],
        },
        created_from: {
            created_at: '2019-01-01T00:00:00.000Z',
            contributor: 'Contributor A',
        },
        sector: [
            {
                updated_at: '2020-01-01T00:00:00.000Z',
                contributor_id: 1,
                contributor_name: 'Contributor A',
                values: ['Apparel'],
                is_from_claim: false,
                created_at: '2020-01-01T00:00:00.000Z',
            },
        ],
        is_claimed: false,
    },
};

describe('getVisibleFields', () => {
    it('returns empty array when data is null', () => {
        expect(getVisibleFields(null)).toEqual([]);
    });

    it('returns empty array when data is undefined', () => {
        expect(getVisibleFields(undefined)).toEqual([]);
    });

    it('returns empty array when data is falsy', () => {
        expect(getVisibleFields(null)).toEqual([]);
        expect(getVisibleFields(undefined)).toEqual([]);
    });

    it('returns visible fields with correct structure (keys and labels)', () => {
        const result = getVisibleFields(anonymizedFacilityData, false);
        expect(Array.isArray(result)).toBe(true);
        result.forEach(field => {
            expect(field).toHaveProperty('key');
            expect(field).toHaveProperty('label');
            expect(field).toHaveProperty('value');
            expect(field.value).not.toBeNull();
            expect(field.value).not.toBeUndefined();
        });
    });

    it('returns fields in config order: name, sector, extended, status', () => {
        const result = getVisibleFields(anonymizedFacilityData, false);
        const keys = result.map(f => f.key);
        expect(keys[0]).toBe('name');
        expect(keys[1]).toBe('sector');
        expect(keys[keys.length - 1]).toBe('status');
    });

    it('excludes additional identifier fields when includeAdditionalIdentifiers is false', () => {
        const result = getVisibleFields(anonymizedFacilityData, false);
        const keys = result.map(f => f.key);
        expect(keys).not.toContain('duns_id');
        expect(keys).not.toContain('lei_id');
        expect(keys).not.toContain('rba_id');
    });

    it('includes additional identifier fields when includeAdditionalIdentifiers is true', () => {
        const result = getVisibleFields(anonymizedFacilityData, true);
        const keys = result.map(f => f.key);
        expect(keys).toContain('rba_id');
    });

    it('preserves current behavior: visible field keys without additional identifiers', () => {
        const result = getVisibleFields(anonymizedFacilityData, false);
        expect(result.map(f => f.key)).toEqual([
            'name',
            'sector',
            'parent_company',
            'processing_type',
            'facility_type',
            'product_type',
            'number_of_workers',
            'isic_4',
            'status',
        ]);
    });

    it('preserves current behavior: visible field keys with additional identifiers', () => {
        const result = getVisibleFields(anonymizedFacilityData, true);
        expect(result.map(f => f.key)).toEqual([
            'name',
            'sector',
            'parent_company',
            'processing_type',
            'facility_type',
            'product_type',
            'number_of_workers',
            'rba_id',
            'isic_4',
            'status',
        ]);
    });
});
