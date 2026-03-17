import {
    getEnrichedPartnerGroups,
    getVisiblePartnerGroups,
} from '../../selectors/partnerFieldGroupsSelectors';

const makeFieldEntry = (fieldName, value = 'test-value') => [
    {
        value,
        created_at: '2025-06-01T00:00:00Z',
        contributor_name: 'Partner',
        contributor_id: 1,
        is_from_claim: false,
        is_verified: false,
        field_name: fieldName,
    },
];

const makeGroup = (partnerFieldNames, overrides = {}) => ({
    uuid: 'group-1',
    name: 'Test Group',
    partner_fields: partnerFieldNames,
    ...overrides,
});

const makeState = (partnerFields = {}, groups = [], groupsFetching = false) => ({
    partnerFieldGroups: {
        data: { results: groups },
        fetching: groupsFetching,
    },
    facilities: {
        singleFacility: {
            data: {
                properties: { partner_fields: partnerFields },
            },
        },
    },
});

const makeEmptyFacilityState = (groups = []) => ({
    partnerFieldGroups: {
        data: { results: groups },
        fetching: false,
    },
    facilities: {
        singleFacility: { data: null },
    },
});

describe('getEnrichedPartnerGroups', () => {
    it('attaches matching partner fields to each group', () => {
        const state = makeState(
            {
                climate_trace: makeFieldEntry('climate_trace'),
                water_usage: makeFieldEntry('water_usage'),
            },
            [makeGroup(['climate_trace', 'water_usage'])],
        );

        const result = getEnrichedPartnerGroups(state);

        expect(result).toHaveLength(1);
        expect(result[0].partnerFields).toHaveLength(2);
        expect(result[0].partnerFields.map(f => f.fieldName)).toEqual(
            expect.arrayContaining(['climate_trace', 'water_usage']),
        );
    });

    it('returns empty partnerFields when group fields do not match facility data', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace') },
            [makeGroup(['nonexistent_field'])],
        );

        const result = getEnrichedPartnerGroups(state);

        expect(result[0].partnerFields).toEqual([]);
    });

    it('preserves original group properties', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace') },
            [makeGroup(['climate_trace'], { uuid: 'custom-id', name: 'Custom Group' })],
        );

        const result = getEnrichedPartnerGroups(state);

        expect(result[0].uuid).toBe('custom-id');
        expect(result[0].name).toBe('Custom Group');
    });

    it('handles multiple groups with different field filters', () => {
        const state = makeState(
            {
                climate_trace: makeFieldEntry('climate_trace'),
                water_usage: makeFieldEntry('water_usage'),
            },
            [
                makeGroup(['climate_trace'], { uuid: 'g1' }),
                makeGroup(['water_usage'], { uuid: 'g2' }),
                makeGroup(['climate_trace', 'water_usage'], { uuid: 'g3' }),
            ],
        );

        const result = getEnrichedPartnerGroups(state);

        expect(result[0].partnerFields).toHaveLength(1);
        expect(result[0].partnerFields[0].fieldName).toBe('climate_trace');
        expect(result[1].partnerFields).toHaveLength(1);
        expect(result[1].partnerFields[0].fieldName).toBe('water_usage');
        expect(result[2].partnerFields).toHaveLength(2);
    });

    it('returns groups with empty partnerFields when facilityData is null', () => {
        const state = makeEmptyFacilityState([makeGroup(['climate_trace'])]);

        const result = getEnrichedPartnerGroups(state);

        expect(result).toHaveLength(1);
        expect(result[0].partnerFields).toEqual([]);
    });

    it('returns an empty array when groups list is empty', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace') },
            [],
        );

        expect(getEnrichedPartnerGroups(state)).toEqual([]);
    });

    it('defaults groups to empty array when data is null', () => {
        const state = {
            partnerFieldGroups: { data: null, fetching: false },
            facilities: { singleFacility: { data: null } },
        };

        expect(getEnrichedPartnerGroups(state)).toEqual([]);
    });

    it('is memoized across identical calls', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace') },
            [makeGroup(['climate_trace'])],
        );

        expect(getEnrichedPartnerGroups(state)).toBe(
            getEnrichedPartnerGroups(state),
        );
    });
});

describe('getVisiblePartnerGroups', () => {
    it('includes groups that have at least one field with a truthy value', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace', 'some-value') },
            [makeGroup(['climate_trace'])],
        );

        const result = getVisiblePartnerGroups(state);

        expect(result).toHaveLength(1);
        expect(result[0].uuid).toBe('group-1');
    });

    it('excludes groups whose fields all have empty values', () => {
        const state = makeState(
            { climate_trace: [] },
            [makeGroup(['climate_trace'])],
        );

        const result = getVisiblePartnerGroups(state);

        expect(result).toEqual([]);
    });

    it('excludes groups whose fields have a falsy first entry', () => {
        const state = makeState(
            { climate_trace: [null] },
            [makeGroup(['climate_trace'])],
        );

        const result = getVisiblePartnerGroups(state);

        expect(result).toEqual([]);
    });

    it('excludes groups with no matching field definitions', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace') },
            [makeGroup(['nonexistent_field'])],
        );

        const result = getVisiblePartnerGroups(state);

        expect(result).toEqual([]);
    });

    it('filters a mix of visible and invisible groups', () => {
        const state = makeState(
            {
                climate_trace: makeFieldEntry('climate_trace'),
                water_usage: [],
            },
            [
                makeGroup(['climate_trace'], { uuid: 'visible' }),
                makeGroup(['water_usage'], { uuid: 'invisible' }),
            ],
        );

        const result = getVisiblePartnerGroups(state);

        expect(result).toHaveLength(1);
        expect(result[0].uuid).toBe('visible');
    });

    it('includes a group if at least one of its fields has data, even if others are empty', () => {
        const state = makeState(
            {
                climate_trace: makeFieldEntry('climate_trace'),
                water_usage: [],
            },
            [makeGroup(['climate_trace', 'water_usage'])],
        );

        const result = getVisiblePartnerGroups(state);

        expect(result).toHaveLength(1);
    });

    it('returns empty array when facilityData is null', () => {
        const state = makeEmptyFacilityState([makeGroup(['climate_trace'])]);

        expect(getVisiblePartnerGroups(state)).toEqual([]);
    });

    it('returns empty array when there are no groups', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace') },
            [],
        );

        expect(getVisiblePartnerGroups(state)).toEqual([]);
    });

    it('is memoized across identical calls', () => {
        const state = makeState(
            { climate_trace: makeFieldEntry('climate_trace') },
            [makeGroup(['climate_trace'])],
        );

        expect(getVisiblePartnerGroups(state)).toBe(
            getVisiblePartnerGroups(state),
        );
    });
});
