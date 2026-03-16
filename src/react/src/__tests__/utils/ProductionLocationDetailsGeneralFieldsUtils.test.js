import getVisibleFields from '../../components/ProductionLocation/ProductionLocationDetailsGeneralFields/utils';
import { FIELD_CONFIG } from '../../components/ProductionLocation/constants.jsx';

/**
 * Anonymized facility fixture for getVisibleFields tests.
 * Structure preserves behavior; all identifiable data replaced with placeholders.
 */
const fullFacilityFixture = {
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
        other_names: [
            'FACILITY A',
            'Facility A Ltd',
            'Facility A Limited',
            'FACILITY A LTD',
            'FACILITY A LTD.',
        ],
        other_addresses: [
            'Address Line One',
            'Address Line Two',
            'Address Line Three',
        ],
        contributors: [
            { id: 1, name: 'Contributor A (List A)', is_verified: false, contributor_name: 'Contributor A', list_name: 'List A' },
            { id: 2, name: 'Contributor B (List B)', is_verified: false, contributor_name: 'Contributor B', list_name: 'List B' },
            { id: 3, name: 'Contributor C (List C)', is_verified: false, contributor_name: 'Contributor C', list_name: 'List C' },
        ],
        country_name: 'Country X',
        claim_info: null,
        other_locations: [
            { lat: 0, lng: 0, contributor_id: 1, contributor_name: 'Contributor A', notes: null },
            { lat: 0, lng: 0, contributor_id: 2, contributor_name: 'Contributor B', notes: null },
        ],
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
                { value: 'Facility A', field_name: 'name', contributor_id: 1, contributor_name: 'Contributor A', updated_at: '2020-01-01T00:00:00.000Z', created_at: '2020-01-01T00:00:00.000Z' },
                { value: 'FACILITY A', field_name: 'name', contributor_id: 2, contributor_name: 'Contributor B', updated_at: '2020-01-01T00:00:00.000Z', created_at: '2020-01-01T00:00:00.000Z' },
            ],
            address: [],
            number_of_workers: [
                { id: 1, is_verified: false, value: { max: 500, min: 500 }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'number_of_workers', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
            native_language_name: [],
            facility_type: [
                { id: 1, is_verified: false, value: { raw_values: 'Type A', matched_values: [['FACILITY_TYPE', 'EXACT', 'Type A', 'Type A']] }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'facility_type', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
            processing_type: [
                { id: 1, is_verified: false, value: { raw_values: 'Type B', matched_values: [['PROCESSING_TYPE', 'EXACT', 'Type B', 'Type B']] }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'processing_type', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
            product_type: [
                { id: 1, is_verified: false, value: { raw_values: ['Product A'] }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'product_type', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
            parent_company: [
                { id: 1, is_verified: false, value: { name: 'Parent A', raw_value: 'Parent A' }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'parent_company', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
            parent_company_os_id: [
                { id: 1, is_verified: false, value: { raw_values: ['YY0000000000000'] }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'parent_company_os_id', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
            duns_id: [],
            lei_id: [],
            rba_id: [
                { id: 1, is_verified: false, value: { raw_value: 'RBA-001' }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'rba_id', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
            isic_4: [
                { id: 1, is_verified: false, value: { raw_value: [{ class: '2620 - Class A', group: '262 - Group A', section: 'C - Manufacturing', division: '26 - Division A' }] }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Contributor A', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'isic_4', verified_count: 0, source_by: null, unit: null, label: null, base_url: null, display_text: null, json_schema: null },
            ],
        },
        created_from: {
            created_at: '2019-01-01T00:00:00.000Z',
            contributor: 'Contributor A',
        },
        sector: [
            { updated_at: '2020-01-01T00:00:00.000Z', contributor_id: 1, contributor_name: 'Contributor A', values: ['Apparel'], is_from_claim: false, created_at: '2020-01-01T00:00:00.000Z' },
        ],
        is_claimed: false,
        partner_fields: {
            wage_indicator: [
                { id: null, is_verified: false, value: { raw_values: { living_wage_link_national: 'https://example.com/living-wage', living_wage_link_national_text: 'Living Wage', minimum_wage_link_english: 'https://example.com/minimum-wage', minimum_wage_link_english_text: 'Minimum Wage', minimum_wage_link_national: 'https://example.com/min-wage', minimum_wage_link_national_text: 'Minimum Wage (national)' } }, created_at: '2020-01-01T00:00:00.000Z', updated_at: '2020-01-01T00:00:00.000Z', contributor_name: 'Test Contributor', contributor_id: 1, value_count: 1, is_from_claim: false, field_name: 'wage_indicator', verified_count: 0, source_by: 'Example source', unit: '', label: '', base_url: '', display_text: '', json_schema: { type: 'object', title: 'Wage indicator reference links', $schema: 'https://json-schema.org/draft/2020-12/schema', properties: { living_wage_link_national: { type: 'string', format: 'uri' }, minimum_wage_link_english: { type: 'string', format: 'uri' }, minimum_wage_link_national: { type: 'string', format: 'uri' }, living_wage_link_national_text: { type: 'string' }, minimum_wage_link_english_text: { type: 'string' }, minimum_wage_link_national_text: { type: 'string' } } } },
            ],
        },
    },
};

describe('getVisibleFields', () => {
    describe('falsy input', () => {
        it('returns exactly empty array when data is null', () => {
            expect(getVisibleFields(null)).toEqual([]);
        });

        it('returns exactly empty array when data is undefined', () => {
            expect(getVisibleFields(undefined)).toEqual([]);
        });

        it('returns exactly empty array when data is false', () => {
            expect(getVisibleFields(false)).toEqual([]);
        });
    });

    describe('minimal input (single visible field)', () => {
        it('returns exactly one field (name) when only name and created_from exist', () => {
            const data = {
                type: 'Feature',
                properties: {
                    name: 'Only Name',
                    created_from: {
                        created_at: '2020-06-15T12:00:00.000Z',
                        contributor: 'Source',
                    },
                    sector: [],
                    extended_fields: {},
                    activity_reports: [],
                },
            };
            const result = getVisibleFields(data, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result).toHaveLength(1);
            expect(result[0]).toEqual({
                key: 'name',
                label: FIELD_CONFIG.name.label,
                value: 'Only Name',
                tooltipText: FIELD_CONFIG.name.tooltipText,
                statusLabel: 'Crowdsourced',
                contributorName: 'Source',
                userId: undefined,
                date: '2020-06-15T12:00:00.000Z',
                drawerData: {
                    promotedContribution: {
                        value: 'Only Name',
                        sourceName: 'Source',
                        date: '2020-06-15T12:00:00.000Z',
                        userId: undefined,
                    },
                    contributions: [],
                },
            });
        });
    });

    describe('name and sector only', () => {
        it('returns exactly two fields in order with full structure', () => {
            const data = {
                type: 'Feature',
                properties: {
                    name: 'Facility',
                    created_from: { created_at: '', contributor: '' },
                    sector: [
                        {
                            contributor_id: 10,
                            contributor_name: 'Org',
                            values: ['Apparel'],
                            created_at: '2021-01-01T00:00:00.000Z',
                            updated_at: '2021-01-01T00:00:00.000Z',
                            is_from_claim: false,
                        },
                    ],
                    extended_fields: { name: [] },
                    activity_reports: [],
                },
            };
            const result = getVisibleFields(data, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result).toHaveLength(2);
            expect(result.map(field => field.key)).toEqual(['name', 'sector']);
            expect(result[0].value).toBe('Facility');
            expect(result[0].drawerData).toEqual({
                promotedContribution: {
                    value: 'Facility',
                    sourceName: null,
                    date: null,
                    userId: undefined,
                },
                contributions: [],
            });
            expect(result[1].value).toBe('Apparel');
            expect(result[1].contributorName).toBe('Org');
            expect(result[1].userId).toBe(10);
            expect(result[1].date).toBe('2021-01-01T00:00:00.000Z');
            expect(result[1].drawerData).toEqual({
                promotedContribution: {
                    value: 'Apparel',
                    sourceName: 'Org',
                    date: '2021-01-01T00:00:00.000Z',
                    userId: 10,
                },
                contributions: [],
            });
        });
    });

    describe('excluded fields', () => {
        it('omits sector when sector array is empty: returns exact single-field array', () => {
            const data = {
                type: 'Feature',
                properties: {
                    name: 'Facility',
                    created_from: { created_at: '', contributor: '' },
                    sector: [],
                    extended_fields: {},
                    activity_reports: [],
                },
            };
            const result = getVisibleFields(data, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result.map(field => field.key)).not.toContain('sector');
            expect(result).toHaveLength(1);
            expect(result[0].key).toBe('name');
        });

        it('omits status when activity_reports is empty: returns exact output without status', () => {
            const data = {
                type: 'Feature',
                properties: {
                    name: 'Facility',
                    created_from: { created_at: '', contributor: '' },
                    sector: [],
                    extended_fields: {},
                    activity_reports: [],
                },
            };
            const result = getVisibleFields(data, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result.map(field => field.key)).not.toContain('status');
        });

        it('omits facility_type when matched_values have null (SKIPPED_MATCHING): returns exact output', () => {
            const data = {
                type: 'Feature',
                properties: {
                    name: 'F',
                    created_from: { created_at: '', contributor: '' },
                    sector: [],
                    extended_fields: {
                        facility_type: [
                            {
                                id: 1,
                                value: {
                                    raw_values: 'X',
                                    matched_values: [
                                        [
                                            'PROCESSING_TYPE',
                                            'SKIPPED_MATCHING',
                                            null,
                                            'X',
                                        ],
                                    ],
                                },
                                contributor_id: 1,
                                contributor_name: 'C',
                                created_at: '2020-01-01T00:00:00.000Z',
                                field_name: 'facility_type',
                            },
                        ],
                    },
                    activity_reports: [],
                },
            };
            const result = getVisibleFields(data, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result.map(field => field.key)).not.toContain('facility_type');
        });

        it('returns exactly empty array when name is null', () => {
            const data = {
                type: 'Feature',
                properties: {
                    name: null,
                    created_from: { created_at: '', contributor: '' },
                    sector: [],
                    extended_fields: {},
                    activity_reports: [],
                },
            };
            const result = getVisibleFields(data, false);
            expect(result).toEqual([]);
        });
    });

    describe('includeAdditionalIdentifiers', () => {
        it('returns exact output when includeAdditionalIdentifiers is false (no duns_id, lei_id, rba_id)', () => {
            const result = getVisibleFields(fullFacilityFixture, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            const keys = result.map(field => field.key);
            expect(keys).not.toContain('duns_id');
            expect(keys).not.toContain('lei_id');
            expect(keys).not.toContain('rba_id');
        });

        it('returns exact output when includeAdditionalIdentifiers is true (includes rba_id)', () => {
            const result = getVisibleFields(fullFacilityFixture, true);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            const rbaField = result.find(field => field.key === 'rba_id');
            expect(rbaField).toBeDefined();
            expect(rbaField.value).toBe('RBA-001');
            expect(rbaField.label).toBe(FIELD_CONFIG.rba_id.label);
        });
    });

    describe('exact full output (full fixture)', () => {
        const expectedKeysWithoutRba = [
            'name',
            'parent_company',
            'sector',
            'product_type',
            'facility_type',
            'processing_type',
            'number_of_workers',
            'parent_company_os_id',
            'isic_4',
            'status',
        ];
        const expectedKeysWithRba = [
            'name',
            'parent_company',
            'sector',
            'product_type',
            'facility_type',
            'processing_type',
            'number_of_workers',
            'parent_company_os_id',
            'isic_4',
            'rba_id',
            'status',
        ];

        it('returns exact full array when includeAdditionalIdentifiers is false', () => {
            const result = getVisibleFields(fullFacilityFixture, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result).toHaveLength(expectedKeysWithoutRba.length);
            expect(result.map(field => field.key)).toEqual(expectedKeysWithoutRba);
            expect(result[0].value).toBe('Facility A');
            expect(result[1].value).toBe('Parent A');
            expect(result[2].value).toBe('Apparel');
            expect(result[6].value).toBe('500');
            expect(result[result.length - 1].value).toBe('Verified closed');
            expect(result[result.length - 1].key).toBe('status');
        });

        it('returns exact full array when includeAdditionalIdentifiers is true', () => {
            const result = getVisibleFields(fullFacilityFixture, true);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result).toHaveLength(expectedKeysWithRba.length);
            expect(result.map(field => field.key)).toEqual(expectedKeysWithRba);
            const rbaIndex = result.findIndex(field => field.key === 'rba_id');
            expect(rbaIndex).toBe(9);
            expect(result[rbaIndex].value).toBe('RBA-001');
        });
    });

    describe('status field from activity_reports', () => {
        it('returns exact full output with status (Verified and Reported) from CONFIRMED report', () => {
            const data = {
                type: 'Feature',
                properties: {
                    name: 'F',
                    created_from: { created_at: '', contributor: '' },
                    sector: [],
                    extended_fields: {},
                    activity_reports: [
                        {
                            status: 'CONFIRMED',
                            closure_state: 'CLOSED',
                            status_change_date: '2022-03-01T00:00:00.000Z',
                            created_at: '2022-02-01T00:00:00.000Z',
                            reported_by_contributor: 'Reporter',
                        },
                    ],
                },
            };
            const result = getVisibleFields(data, false);
            const expected = result.map(field => ({
                ...field,
                label: FIELD_CONFIG[field.key].label,
                tooltipText: FIELD_CONFIG[field.key].tooltipText,
            }));
            expect(result).toEqual(expected);
            expect(result.map(field => field.key)).toEqual(['name', 'status']);
            const statusField = result.find(field => field.key === 'status');
            expect(statusField.value).toBe('Verified closed');
            expect(statusField.drawerData.promotedContribution.value).toBe(
                'Verified closed',
            );
            expect(statusField.drawerData.contributions).toHaveLength(1);
            expect(statusField.drawerData.contributions[0].value).toBe(
                'Reported closed',
            );
            expect(statusField.drawerData.contributions[0].sourceName).toBe(
                'Reporter',
            );
        });
    });
});
