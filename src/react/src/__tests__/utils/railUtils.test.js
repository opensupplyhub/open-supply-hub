/* eslint-env jest */

import {
    buildQueueGroups,
    nextVisibleClaimID,
    matchesQuery,
    regionOptions,
    claimAgeDays,
    ALL_REGIONS,
    SORT_ORDERS,
} from '../../components/ClaimsV2/railUtils';
import { CLAIM_STAGES } from '../../components/ClaimsV2/stageUtils';

// Fixed "now": Wednesday 2026-09-30T12:00:00Z.
const NOW = new Date('2026-09-30T12:00:00Z');

const claim = (id, overrides = {}) => ({
    id,
    facility_name: `Facility ${id}`,
    facility_country_name: 'United States',
    contributor_name: 'A Contributor',
    os_id: `US2026TEST${id}`,
    created_at: '2026-09-01T00:00:00Z',
    notes_meta: [],
    ...overrides,
});

// notes_meta shapes: no message => new; recent message => awaiting;
// old message => overdue (15 business days promised).
const messagedAt = iso => [
    { note_type: 'CLAIMANT_MESSAGE', created_at: iso },
];

describe('buildQueueGroups', () => {
    it('groups claims into stages derived from notes_meta', () => {
        const claims = [
            claim(1),
            claim(2, { notes_meta: messagedAt('2026-09-28T00:00:00Z') }),
            claim(3, { notes_meta: messagedAt('2026-08-01T00:00:00Z') }),
        ];
        const { groups } = buildQueueGroups(claims, { now: NOW });

        expect(groups[CLAIM_STAGES.NEW].map(c => c.id)).toEqual([1]);
        expect(groups[CLAIM_STAGES.AWAITING].map(c => c.id)).toEqual([2]);
        expect(groups[CLAIM_STAGES.OVERDUE].map(c => c.id)).toEqual([3]);
    });

    it('attaches stageInfo so cards can render waiting badges', () => {
        const { groups } = buildQueueGroups(
            [claim(2, { notes_meta: messagedAt('2026-09-28T00:00:00Z') })],
            { now: NOW },
        );
        const [awaiting] = groups[CLAIM_STAGES.AWAITING];
        expect(awaiting.stageInfo.stage).toBe(CLAIM_STAGES.AWAITING);
        expect(awaiting.stageInfo.waitingBusinessDays).toBeGreaterThan(0);
    });

    it('sorts oldest-first by default and newest-first when asked', () => {
        const claims = [
            claim(1, { created_at: '2026-09-05T00:00:00Z' }),
            claim(2, { created_at: '2026-09-01T00:00:00Z' }),
        ];
        const oldest = buildQueueGroups(claims, { now: NOW });
        expect(oldest.groups[CLAIM_STAGES.NEW].map(c => c.id)).toEqual([2, 1]);

        const newest = buildQueueGroups(claims, {
            now: NOW,
            sort: SORT_ORDERS.NEWEST,
        });
        expect(newest.groups[CLAIM_STAGES.NEW].map(c => c.id)).toEqual([1, 2]);
    });

    it('filters by query and by region', () => {
        const claims = [
            claim(1, { facility_name: 'Alpha Mill' }),
            claim(2, {
                facility_name: 'Beta Works',
                facility_country_name: 'Bangladesh',
            }),
        ];
        const byQuery = buildQueueGroups(claims, { now: NOW, query: 'beta' });
        expect(byQuery.visibleIds).toEqual([2]);

        const byRegion = buildQueueGroups(claims, {
            now: NOW,
            region: 'Bangladesh',
        });
        expect(byRegion.visibleIds).toEqual([2]);
    });

    it('flattens visibleIds in stage order for keyboard navigation', () => {
        const claims = [
            claim(3, { notes_meta: messagedAt('2026-08-01T00:00:00Z') }),
            claim(2, { notes_meta: messagedAt('2026-09-28T00:00:00Z') }),
            claim(1),
        ];
        const { visibleIds } = buildQueueGroups(claims, { now: NOW });
        expect(visibleIds).toEqual([1, 2, 3]);
    });

    it('handles claims with missing notes_meta as new', () => {
        const { groups } = buildQueueGroups(
            [claim(9, { notes_meta: undefined })],
            { now: NOW },
        );
        expect(groups[CLAIM_STAGES.NEW].map(c => c.id)).toEqual([9]);
    });
});

describe('nextVisibleClaimID', () => {
    it('moves forward and backward, clamping at the ends', () => {
        const ids = [1, 2, 3];
        expect(nextVisibleClaimID(ids, 1, 1)).toBe(2);
        expect(nextVisibleClaimID(ids, 2, -1)).toBe(1);
        expect(nextVisibleClaimID(ids, 3, 1)).toBe(3);
        expect(nextVisibleClaimID(ids, 1, -1)).toBe(1);
    });

    it('enters at the top with no selection or a filtered-out one', () => {
        expect(nextVisibleClaimID([1, 2], null, 1)).toBe(1);
        expect(nextVisibleClaimID([1, 2], 99, -1)).toBe(1);
        expect(nextVisibleClaimID([], null, 1)).toBeNull();
    });
});

describe('matchesQuery', () => {
    const c = claim(42, { facility_name: 'Sunrise Textiles' });

    it('matches name, id, contributor, country, and os_id', () => {
        expect(matchesQuery(c, 'sunrise')).toBe(true);
        expect(matchesQuery(c, '42')).toBe(true);
        expect(matchesQuery(c, 'contributor')).toBe(true);
        expect(matchesQuery(c, 'united')).toBe(true);
        expect(matchesQuery(c, 'US2026TEST42')).toBe(true);
        expect(matchesQuery(c, 'zzz')).toBe(false);
    });

    it('treats empty or whitespace queries as match-all', () => {
        expect(matchesQuery(c, '')).toBe(true);
        expect(matchesQuery(c, '   ')).toBe(true);
    });
});

describe('regionOptions', () => {
    it('returns All regions plus unique sorted country names', () => {
        const options = regionOptions([
            claim(1, { facility_country_name: 'Vietnam' }),
            claim(2, { facility_country_name: 'Bangladesh' }),
            claim(3, { facility_country_name: 'Vietnam' }),
        ]);
        expect(options).toEqual([ALL_REGIONS, 'Bangladesh', 'Vietnam']);
    });
});

describe('claimAgeDays', () => {
    it('floors to whole days and never goes negative', () => {
        expect(claimAgeDays('2026-09-28T11:00:00Z', NOW)).toBe(2);
        expect(claimAgeDays('2026-10-05T00:00:00Z', NOW)).toBe(0);
        expect(claimAgeDays('not a date', NOW)).toBe(0);
    });
});
