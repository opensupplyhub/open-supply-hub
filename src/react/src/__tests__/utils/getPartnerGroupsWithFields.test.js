import getPartnerGroupsWithFields from '../../components/ProductionLocation/PartnerSection/PartnerDataContainer/utils';

const makeFacilityData = (partnerFields = {}) => ({
    properties: { partner_fields: partnerFields },
});

const makeGroup = (partnerFieldNames, overrides = {}) => ({
    uuid: 'group-1',
    name: 'Test Group',
    partner_fields: partnerFieldNames,
    ...overrides,
});

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

describe('getPartnerGroupsWithFields', () => {
    it('attaches matching partner fields to each group', () => {
        const facilityData = makeFacilityData({
            climate_trace: makeFieldEntry('climate_trace'),
            water_usage: makeFieldEntry('water_usage'),
        });
        const groups = [makeGroup(['climate_trace', 'water_usage'])];

        const result = getPartnerGroupsWithFields(facilityData, groups);

        expect(result).toHaveLength(1);
        expect(result[0].partnerFields).toHaveLength(2);
        expect(result[0].partnerFields.map(f => f.fieldName)).toEqual(
            expect.arrayContaining(['climate_trace', 'water_usage']),
        );
    });

    it('returns empty partnerFields when group fields do not match any facility data', () => {
        const facilityData = makeFacilityData({
            climate_trace: makeFieldEntry('climate_trace'),
        });
        const groups = [makeGroup(['nonexistent_field'])];

        const result = getPartnerGroupsWithFields(facilityData, groups);

        expect(result[0].partnerFields).toEqual([]);
    });

    it('preserves original group properties', () => {
        const facilityData = makeFacilityData({
            climate_trace: makeFieldEntry('climate_trace'),
        });
        const groups = [
            makeGroup(['climate_trace'], {
                uuid: 'custom-id',
                name: 'Custom Group',
            }),
        ];

        const result = getPartnerGroupsWithFields(facilityData, groups);

        expect(result[0].uuid).toBe('custom-id');
        expect(result[0].name).toBe('Custom Group');
    });

    it('handles multiple groups with different field filters', () => {
        const facilityData = makeFacilityData({
            climate_trace: makeFieldEntry('climate_trace'),
            water_usage: makeFieldEntry('water_usage'),
        });
        const groups = [
            makeGroup(['climate_trace'], { uuid: 'g1' }),
            makeGroup(['water_usage'], { uuid: 'g2' }),
            makeGroup(['climate_trace', 'water_usage'], { uuid: 'g3' }),
        ];

        const result = getPartnerGroupsWithFields(facilityData, groups);

        expect(result[0].partnerFields).toHaveLength(1);
        expect(result[0].partnerFields[0].fieldName).toBe('climate_trace');
        expect(result[1].partnerFields).toHaveLength(1);
        expect(result[1].partnerFields[0].fieldName).toBe('water_usage');
        expect(result[2].partnerFields).toHaveLength(2);
    });

    it('returns groups with empty partnerFields when facilityData is null', () => {
        const groups = [makeGroup(['climate_trace'])];

        const result = getPartnerGroupsWithFields(null, groups);

        expect(result).toHaveLength(1);
        expect(result[0].partnerFields).toEqual([]);
    });

    it('returns groups with empty partnerFields when partner_fields property is missing', () => {
        const facilityData = { properties: {} };
        const groups = [makeGroup(['climate_trace'])];

        const result = getPartnerGroupsWithFields(facilityData, groups);

        expect(result).toHaveLength(1);
        expect(result[0].partnerFields).toEqual([]);
    });

    it('returns an empty array when groups is empty', () => {
        const facilityData = makeFacilityData({
            climate_trace: makeFieldEntry('climate_trace'),
        });

        const result = getPartnerGroupsWithFields(facilityData, []);

        expect(result).toEqual([]);
    });
});
