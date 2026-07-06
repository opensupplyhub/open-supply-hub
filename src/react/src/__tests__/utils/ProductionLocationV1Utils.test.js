import {
    getV1HighlightedField,
    normalizeDisplayValue,
} from '../../components/ProductionLocation/utils';

describe('getV1HighlightedField', () => {
    const v1Data = {
        os_id: 'XX0000000000000',
        name: 'Claimant Facility Name',
        name_source: {
            contributor_id: 42,
            contributor_name: 'Claimant Org',
            contributed_at: '2024-05-01T00:00:00Z',
            is_claimed_data: true,
            is_promoted: false,
            is_verified: false,
        },
        location_type: ['Final Product Assembly'],
        location_type_source: {
            contributor_id: 7,
            contributor_name: 'Other Org',
            contributed_at: '2024-01-01T00:00:00Z',
            is_claimed_data: false,
            is_promoted: true,
            is_verified: false,
        },
        number_of_workers: { min: 100, max: 200 },
        number_of_workers_source: {
            contributor_id: 42,
            contributor_name: 'Claimant Org',
            contributed_at: '2024-05-01T00:00:00Z',
            is_claimed_data: true,
            is_promoted: false,
            is_verified: false,
        },
        parent_company: 'Parent Co',
    };

    it('returns null when v1Data is missing', () => {
        expect(getV1HighlightedField(null, 'name')).toBeNull();
        expect(getV1HighlightedField(undefined, 'name')).toBeNull();
    });

    it('returns null for fields without a v1 mapping', () => {
        expect(getV1HighlightedField(v1Data, 'isic_4')).toBeNull();
        expect(getV1HighlightedField(v1Data, 'parent_company_os_id')).toBeNull();
    });

    it('returns null when the *_source attribution object is absent', () => {
        // parent_company has a value but no parent_company_source, e.g. a
        // document indexed before attribution fields were introduced.
        expect(getV1HighlightedField(v1Data, 'parent_company')).toBeNull();
    });

    it('returns the value with attribution for a claimed field', () => {
        expect(getV1HighlightedField(v1Data, 'name')).toEqual({
            value: 'Claimant Facility Name',
            sourceName: 'Claimant Org',
            userId: 42,
            date: '2024-05-01T00:00:00Z',
            isClaimedData: true,
        });
    });

    it('maps facility_type to the v1 location_type field', () => {
        expect(getV1HighlightedField(v1Data, 'facility_type')).toEqual({
            value: ['Final Product Assembly'],
            sourceName: 'Other Org',
            userId: 7,
            date: '2024-01-01T00:00:00Z',
            isClaimedData: false,
        });
    });

    it('formats number_of_workers as a min-max range', () => {
        expect(getV1HighlightedField(v1Data, 'number_of_workers').value).toBe(
            '100-200',
        );
    });

    it('formats number_of_workers as a single value when min equals max', () => {
        const singleValue = {
            ...v1Data,
            number_of_workers: { min: 300, max: 300 },
        };
        expect(
            getV1HighlightedField(singleValue, 'number_of_workers').value,
        ).toBe('300');
    });

    it('returns null when the value is empty', () => {
        const empty = {
            ...v1Data,
            name: '   ',
            location_type: [],
            number_of_workers: {},
        };
        expect(getV1HighlightedField(empty, 'name')).toBeNull();
        expect(getV1HighlightedField(empty, 'facility_type')).toBeNull();
        expect(getV1HighlightedField(empty, 'number_of_workers')).toBeNull();
    });
});

describe('normalizeDisplayValue', () => {
    it('normalizes strings by trimming and lowercasing', () => {
        expect(normalizeDisplayValue('  Facility A ')).toBe('facility a');
        expect(normalizeDisplayValue('FACILITY A')).toBe(
            normalizeDisplayValue('Facility A'),
        );
    });

    it('normalizes arrays ignoring order, casing and duplicates', () => {
        expect(normalizeDisplayValue(['B', 'a'])).toBe(
            normalizeDisplayValue(['A ', 'b', 'a']),
        );
    });

    it('distinguishes different values', () => {
        expect(normalizeDisplayValue('Facility A')).not.toBe(
            normalizeDisplayValue('Facility B'),
        );
        expect(normalizeDisplayValue(['A'])).not.toBe(
            normalizeDisplayValue(['A', 'B']),
        );
    });

    it('handles null and undefined', () => {
        expect(normalizeDisplayValue(null)).toBe('');
        expect(normalizeDisplayValue(undefined)).toBe('');
    });
});
