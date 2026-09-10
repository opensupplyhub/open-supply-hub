/*
 * Queue rail logic for claims dashboard v2 (OSDEV-3356): stage
 * grouping, client-side search, region filter, sort, and the flat
 * visible-id order that J/K navigation walks.
 *
 * Pure functions over the claims-list payload; stages come from
 * deriveClaimStage over the list serializer's notes_meta.
 */

import { deriveClaimStage, CLAIM_STAGES } from './stageUtils';

export const SORT_ORDERS = Object.freeze({
    OLDEST: 'oldest',
    NEWEST: 'newest',
});

// Section order in the rail — matches the prototype: work the new
// claims, then the waiting ones, with overdue decisions at the bottom
// anchor of the rail.
export const STAGE_ORDER = Object.freeze([
    CLAIM_STAGES.NEW,
    CLAIM_STAGES.AWAITING,
    CLAIM_STAGES.OVERDUE,
]);

const DAY_MS = 24 * 60 * 60 * 1000;

export const claimAgeDays = (createdAt, now = new Date()) => {
    const created = new Date(createdAt);
    if (Number.isNaN(created.getTime())) {
        return 0;
    }
    return Math.max(0, Math.floor((now - created) / DAY_MS));
};

/*
 * Case-insensitive match over the fields a moderator would type from
 * memory: facility name, claim id, contributor, and country.
 */
export const matchesQuery = (claim, query) => {
    const needle = (query || '').trim().toLowerCase();
    if (!needle) {
        return true;
    }
    return [
        claim.facility_name,
        String(claim.id),
        claim.contributor_name,
        claim.facility_country_name,
        claim.os_id,
    ].some(value => (value || '').toString().toLowerCase().includes(needle));
};

export const ALL_REGIONS = 'All regions';

export const regionOptions = claims => {
    const names = new Set();
    (claims || []).forEach(claim => {
        if (claim.facility_country_name) {
            names.add(claim.facility_country_name);
        }
    });
    return [ALL_REGIONS, ...Array.from(names).sort()];
};

/*
 * Filter, stage, and sort the pending claims into rail sections.
 *
 * Returns { groups, visibleIds }:
 *   groups     — { [stage]: [claim, ...] } where each claim carries a
 *                `stageInfo` ({ stage, reason, waitingBusinessDays, ... })
 *                so cards can render waiting badges without re-deriving.
 *   visibleIds — claim ids flattened in on-screen order (STAGE_ORDER,
 *                then the sort inside each section): the J/K walk order.
 */
export const buildQueueGroups = (
    claims,
    {
        query = '',
        region = ALL_REGIONS,
        sort = SORT_ORDERS.OLDEST,
        now = new Date(),
    } = {},
) => {
    const groups = {};
    STAGE_ORDER.forEach(stage => {
        groups[stage] = [];
    });

    (claims || [])
        .filter(claim => matchesQuery(claim, query))
        .filter(
            claim =>
                region === ALL_REGIONS ||
                claim.facility_country_name === region,
        )
        .forEach(claim => {
            const stageInfo = deriveClaimStage(claim.notes_meta, { now });
            groups[stageInfo.stage].push({ ...claim, stageInfo });
        });

    const direction = sort === SORT_ORDERS.OLDEST ? 1 : -1;
    STAGE_ORDER.forEach(stage => {
        groups[stage].sort(
            (a, b) =>
                direction * (new Date(a.created_at) - new Date(b.created_at)),
        );
    });

    const visibleIds = STAGE_ORDER.reduce(
        (ids, stage) => ids.concat(groups[stage].map(claim => claim.id)),
        [],
    );

    return { groups, visibleIds };
};

/*
 * The id J/K navigation should move to: `delta` of +1/-1 from the
 * current selection within visibleIds. With nothing selected (or the
 * selection filtered out), both directions enter the list at the top.
 */
export const nextVisibleClaimID = (visibleIds, selectedClaimID, delta) => {
    if (!visibleIds || visibleIds.length === 0) {
        return null;
    }
    const currentIndex = visibleIds.indexOf(selectedClaimID);
    if (currentIndex === -1) {
        return visibleIds[0];
    }
    const nextIndex = Math.min(
        visibleIds.length - 1,
        Math.max(0, currentIndex + delta),
    );
    return visibleIds[nextIndex];
};
