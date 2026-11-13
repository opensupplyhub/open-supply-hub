/* eslint-env jest */

import {
    forgetClaimCampaignCode,
    getClaimCampaignCode,
    isActiveClaimCampaign,
    makeClaimCampaignLookupURL,
    normalizeCampaignCode,
    rememberClaimCampaignCode,
} from '../../util/claimCampaign';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
}));

const OS_ID = 'US2026295YQM9BZ';
const DAY_MS = 24 * 60 * 60 * 1000;

describe('normalizeCampaignCode', () => {
    test('upper-cases and trims a valid code', () => {
        expect(normalizeCampaignCode('  meridian-x7k2qp ')).toBe(
            'MERIDIAN-X7K2QP',
        );
    });

    test.each([
        ['empty', ''],
        ['missing', null],
        ['leading hyphen', '-ABC'],
        ['bad characters', 'ABC&campaign=1'],
        ['spaces inside', 'ABC DEF'],
        ['over 50 characters', 'A'.repeat(51)],
    ])('rejects a code that is %s', (_, value) => {
        expect(normalizeCampaignCode(value)).toBeNull();
    });

    test('accepts a 50-character code', () => {
        expect(normalizeCampaignCode('A'.repeat(50))).toBe('A'.repeat(50));
    });
});

describe('claim campaign code storage', () => {
    let now;

    beforeEach(() => {
        // The test environment is node, which has no localStorage.
        const store = {};
        global.localStorage = {
            getItem: key => (key in store ? store[key] : null),
            setItem: (key, value) => {
                store[key] = String(value);
            },
            removeItem: key => {
                delete store[key];
            },
        };
        now = Date.now();
        jest.spyOn(Date, 'now').mockImplementation(() => now);
    });

    afterEach(() => {
        jest.restoreAllMocks();
        delete global.localStorage;
    });

    test('remembers a code per production location', () => {
        rememberClaimCampaignCode(OS_ID, 'MERIDIAN-X7K2QP');

        expect(getClaimCampaignCode(OS_ID)).toBe('MERIDIAN-X7K2QP');
        expect(getClaimCampaignCode('OTHER')).toBeNull();
    });

    test('lapses after a week', () => {
        rememberClaimCampaignCode(OS_ID, 'MERIDIAN-X7K2QP');
        now += 8 * DAY_MS;

        expect(getClaimCampaignCode(OS_ID)).toBeNull();
    });

    test('forgets a code', () => {
        rememberClaimCampaignCode(OS_ID, 'MERIDIAN-X7K2QP');
        forgetClaimCampaignCode(OS_ID);

        expect(getClaimCampaignCode(OS_ID)).toBeNull();
    });

    test('works without storage', () => {
        delete global.localStorage;

        expect(() =>
            rememberClaimCampaignCode(OS_ID, 'MERIDIAN-X7K2QP'),
        ).not.toThrow();
        expect(getClaimCampaignCode(OS_ID)).toBeNull();
    });
});

describe('isActiveClaimCampaign', () => {
    test('encodes the code in the lookup URL', () => {
        expect(makeClaimCampaignLookupURL('A&B')).toBe(
            '/api/claim-campaigns/lookup/?code=A%26B',
        );
    });

    test('reports the backend answer', async () => {
        apiRequest.get.mockResolvedValue({ data: { active: true } });
        await expect(isActiveClaimCampaign('ABC')).resolves.toBe(true);

        apiRequest.get.mockResolvedValue({ data: { active: false } });
        await expect(isActiveClaimCampaign('ABC')).resolves.toBe(false);
    });

    test('reports null when the lookup fails', async () => {
        apiRequest.get.mockRejectedValue(new Error('offline'));
        await expect(isActiveClaimCampaign('ABC')).resolves.toBeNull();
    });
});
