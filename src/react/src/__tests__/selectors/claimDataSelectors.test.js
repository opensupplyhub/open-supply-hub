import {
    getClaimInfo,
    getIsClaimed,
    getClaimDisplayData,
} from '../../selectors/claimDataSelectors';

const makeClaimInfo = (overrides = {}) => ({
    status: 'APPROVED',
    facility: {
        website: 'https://example.com',
        phone_number: '+1 234 567 8900',
        minimum_order: '100 units',
        description: 'A sample facility.',
    },
    contact: { name: 'Jane Doe', email: 'jane@example.com' },
    office: { name: 'Head Office', address: '1 Office St', country: 'US' },
    contributor: { name: 'Test Contributor' },
    user_id: 42,
    approved_at: '2023-05-15',
    created_at: '2023-01-01',
    ...overrides,
});

const makeState = claimInfo => ({
    facilities: {
        singleFacility: {
            data: claimInfo != null
                ? { properties: { claim_info: claimInfo } }
                : null,
        },
    },
});

describe('getClaimInfo', () => {
    it('returns claim_info when present', () => {
        const claimInfo = makeClaimInfo();
        expect(getClaimInfo(makeState(claimInfo))).toBe(claimInfo);
    });

    it('returns null when data is missing', () => {
        expect(getClaimInfo(makeState(null))).toBeNull();
    });
});

describe('getIsClaimed', () => {
    it.each(['APPROVED', 'DENIED', 'REVOKED'])(
        'returns true for %s status',
        status => {
            const state = makeState(makeClaimInfo({ status }));
            expect(getIsClaimed(state)).toBe(true);
        },
    );

    it('returns false for PENDING status', () => {
        expect(getIsClaimed(makeState(makeClaimInfo({ status: 'PENDING' })))).toBe(false);
    });

    it('returns false when claim_info is null', () => {
        expect(getIsClaimed(makeState(null))).toBe(false);
    });
});

describe('getClaimDisplayData', () => {
    it('returns empty data when claim_info is null', () => {
        expect(getClaimDisplayData(makeState(null))).toEqual({
            displayableFields: [],
            contributorName: null,
            contributorUserId: null,
            claimedAt: null,
        });
    });

    it('returns empty data when status is PENDING', () => {
        const result = getClaimDisplayData(
            makeState(makeClaimInfo({ status: 'PENDING' })),
        );
        expect(result.displayableFields).toEqual([]);
    });

    it('extracts contributorName from object', () => {
        const { contributorName } = getClaimDisplayData(
            makeState(makeClaimInfo({ contributor: { name: 'Acme' } })),
        );
        expect(contributorName).toBe('Acme');
    });

    it('uses string contributor directly', () => {
        const { contributorName } = getClaimDisplayData(
            makeState(makeClaimInfo({ contributor: 'Plain Name' })),
        );
        expect(contributorName).toBe('Plain Name');
    });

    it('extracts contributorUserId', () => {
        const { contributorUserId } = getClaimDisplayData(
            makeState(makeClaimInfo({ user_id: 99 })),
        );
        expect(contributorUserId).toBe(99);
    });

    it('prefers approved_at for claimedAt', () => {
        const { claimedAt } = getClaimDisplayData(makeState(makeClaimInfo()));
        expect(claimedAt).toBe('2023-05-15');
    });

    it('falls back to created_at when approved_at is absent', () => {
        const { claimedAt } = getClaimDisplayData(
            makeState(makeClaimInfo({ approved_at: undefined })),
        );
        expect(claimedAt).toBe('2023-01-01');
    });

    it('populates displayableFields for a valid claim', () => {
        const { displayableFields } = getClaimDisplayData(
            makeState(makeClaimInfo()),
        );
        expect(displayableFields.length).toBeGreaterThan(0);

        const field = displayableFields[0];
        expect(field).toHaveProperty('key');
        expect(field).toHaveProperty('label');
        expect(typeof field.getValue).toBe('function');
    });

    it('returns empty fields when facility has no values', () => {
        const { displayableFields } = getClaimDisplayData(
            makeState(makeClaimInfo({ facility: {}, contact: null, office: null })),
        );
        expect(displayableFields).toEqual([]);
    });

    it('sorts fields according to FIELD_ORDER', () => {
        const keys = getClaimDisplayData(makeState(makeClaimInfo()))
            .displayableFields.map(field => field.key);

        expect(keys.indexOf('website')).toBeLessThan(keys.indexOf('phone_number'));
        expect(keys.indexOf('phone_number')).toBeLessThan(keys.indexOf('description'));
    });

    it('is memoized across identical calls', () => {
        const state = makeState(makeClaimInfo());
        expect(getClaimDisplayData(state)).toBe(getClaimDisplayData(state));
    });
});
