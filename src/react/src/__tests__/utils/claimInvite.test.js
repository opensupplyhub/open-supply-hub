/* eslint-env jest */

import {
    rememberClaimInviteCode,
    getClaimInviteCode,
    forgetClaimInviteCode,
} from '../../util/claimInvite';

const OS_ID = 'US2026295YQM9BZ';
const DAY_MS = 24 * 60 * 60 * 1000;

describe('claim invite code storage', () => {
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

    test('remembers the code from an invite link', () => {
        rememberClaimInviteCode(OS_ID, '?invite=abc-123');

        expect(getClaimInviteCode(OS_ID)).toBe('abc-123');
    });

    test('ignores a link without an invite code', () => {
        rememberClaimInviteCode(OS_ID, '?utm_source=email');

        expect(getClaimInviteCode(OS_ID)).toBeNull();
    });

    test('keeps codes separate per production location', () => {
        rememberClaimInviteCode(OS_ID, '?invite=abc-123');

        expect(getClaimInviteCode('CN2026000000000')).toBeNull();
    });

    test('a code lapses after a week', () => {
        rememberClaimInviteCode(OS_ID, '?invite=abc-123');

        now += 6 * DAY_MS;
        expect(getClaimInviteCode(OS_ID)).toBe('abc-123');

        now += 2 * DAY_MS;
        expect(getClaimInviteCode(OS_ID)).toBeNull();
        expect(localStorage.getItem(`claim-invite-${OS_ID}`)).toBeNull();
    });

    test('forgets the code after the claim is sent', () => {
        rememberClaimInviteCode(OS_ID, '?invite=abc-123');
        forgetClaimInviteCode(OS_ID);

        expect(getClaimInviteCode(OS_ID)).toBeNull();
    });

    test('a value stored in an older format is ignored', () => {
        localStorage.setItem(`claim-invite-${OS_ID}`, 'abc-123');

        expect(getClaimInviteCode(OS_ID)).toBeNull();
    });
});
