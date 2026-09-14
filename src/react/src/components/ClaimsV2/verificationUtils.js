/*
 * Verification-panel logic (OSDEV-3356, SPEC.md §5a): tier-1 status
 * chips from the automated review's per-criterion scores, and the
 * client-side organization-name consistency check.
 *
 * Below-threshold is ALWAYS advisory amber, never red — "needs your
 * judgement", not "mismatch". The organization row never renders as a
 * mismatch on string logic alone.
 */

export const CHIP_STATUS = Object.freeze({
    PASS: 'pass',
    CHECK: 'check',
    NONE: 'none',
});

// Matches the pipeline's default; a review may carry its own
// per-criterion thresholds snapshot.
const DEFAULT_THRESHOLD = 0.6;

const round2 = value => Number(value).toFixed(2);

export const scoreChip = (review, key) => {
    const score = review?.scores?.[key];
    if (typeof score !== 'number') {
        return {
            status: CHIP_STATUS.NONE,
            text: 'No automated review — check the documents',
            reasoning: null,
        };
    }
    const threshold =
        typeof review?.thresholds?.[key] === 'number'
            ? review.thresholds[key]
            : DEFAULT_THRESHOLD;
    if (score >= threshold) {
        return {
            status: CHIP_STATUS.PASS,
            text: `✓ ${round2(score)} ≥ ${round2(
                threshold,
            )} · clears threshold`,
            reasoning: null,
        };
    }
    return {
        status: CHIP_STATUS.CHECK,
        text: `⚠ ${round2(score)} < ${round2(threshold)} · below threshold`,
        // The pipeline's reasoning sentence renders under
        // below-threshold rows only (§5a).
        reasoning: review?.reasoning?.[key] || null,
    };
};

export const normalizeOrgName = value =>
    (value || '').toLowerCase().replace(/[^a-z0-9]/g, '');

/*
 * Client-side organization consistency: normalized containment in
 * either direction. Advisory only — a non-match gets the
 * rebrands/parent-companies caveat, never a red state (§5a).
 */
export const orgNamesConsistent = (profileName, statedName) => {
    const profile = normalizeOrgName(profileName);
    const stated = normalizeOrgName(statedName);
    if (!profile || !stated) {
        return false;
    }
    return profile.includes(stated) || stated.includes(profile);
};

/*
 * The organization row combines the affiliation score with the name
 * check: either passing reads "Looks consistent"; neither passing
 * degrades to "needs your judgement" with the provenance caveat.
 */
export const organizationRowStatus = (review, profileName, statedName) => {
    const affiliation = scoreChip(review, 'affiliation');
    const namesMatch = orgNamesConsistent(profileName, statedName);
    if (affiliation.status === CHIP_STATUS.PASS || namesMatch) {
        return {
            status: CHIP_STATUS.PASS,
            text: 'Looks consistent',
            reasoning: null,
        };
    }
    if (affiliation.status === CHIP_STATUS.NONE) {
        return affiliation;
    }
    return {
        status: CHIP_STATUS.CHECK,
        text: '⚠ Needs your judgement',
        reasoning:
            'The stated organization name does not contain (or appear ' +
            'in) the profile name — rebrands and parent companies look ' +
            'like this too, so check the documents.',
    };
};
