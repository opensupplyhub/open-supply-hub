import { makePendingClaimEditLink } from '../../util/util';
import {
    CHECKING_FACTS,
    CHECKING_STEPS,
    CHECK_AGAIN_QUERY_PARAM,
    CLAIM_LIVE_CHECK_FIXES,
    FACT_LABEL_LOCATION,
    FIX_QUERY_PARAM,
} from './constants';

export const prefersReducedMotion = () =>
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// There is no real progress signal, so the bar follows the time passed
// on a curve that reaches 90% at 45 seconds and stops at 95%. Only
// `done` (the result has arrived) fills it.
export const getCheckingProgress = (elapsedMs, done) =>
    done
        ? 100
        : Math.min(95, Math.round(100 * (1 - Math.exp(-elapsedMs / 19543))));

export const STEP_STATES = Object.freeze({
    DONE: 'done',
    NOW: 'now',
    WAITING: 'waiting',
});

// A step is finished once the next one has started, so the last step
// is only ever finished by `done`.
export const getCheckingStepStates = (elapsedMs, done) =>
    CHECKING_STEPS.map((step, index) => {
        const next = CHECKING_STEPS[index + 1];
        if (done || index === 0 || (next && elapsedMs >= next.startsAtMs)) {
            return STEP_STATES.DONE;
        }
        return elapsedMs >= step.startsAtMs
            ? STEP_STATES.NOW
            : STEP_STATES.WAITING;
    });

// The fact about the location is only included when its name and its
// number of contributors are both known.
export const getCheckingFacts = (locationName, contributorCount) => {
    const name = typeof locationName === 'string' ? locationName.trim() : '';
    if (!name || !Number.isInteger(contributorCount) || contributorCount < 1) {
        return CHECKING_FACTS;
    }
    const text =
        contributorCount === 1
            ? `1 organisation has shared data about ${name} on Open Supply Hub.`
            : `${contributorCount} organisations have shared data about ${name} on Open Supply Hub.`;
    return [{ label: FACT_LABEL_LOCATION, text }, ...CHECKING_FACTS];
};

export const getContributorCount = location => {
    if (Number.isInteger(location?.number_of_contributors)) {
        return location.number_of_contributors;
    }
    return Array.isArray(location?.contributors)
        ? location.contributors.length
        : null;
};

const isKnownFix = fix =>
    typeof fix === 'string' &&
    Object.prototype.hasOwnProperty.call(CLAIM_LIVE_CHECK_FIXES, fix);

// The pending claim edit page, opened at the field `fix` is about.
// `canCheckAgain` asks that page to run the check again after saving.
export const makeFixLink = (claimID, fix, canCheckAgain) => {
    const params = new URLSearchParams({ [FIX_QUERY_PARAM]: fix });
    if (canCheckAgain) {
        params.set(CHECK_AGAIN_QUERY_PARAM, '1');
    }
    return `${makePendingClaimEditLink(claimID)}?${params}`;
};

// The query string is user-editable, so `fix` is only ever one of the
// preset keys (or null).
export const parseFixParams = search => {
    const params = new URLSearchParams(search || '');
    const fix = params.get(FIX_QUERY_PARAM);
    return {
        fix: isKnownFix(fix) ? fix : null,
        checkAgain: params.get(CHECK_AGAIN_QUERY_PARAM) === '1',
    };
};

// The fixes grouped by the field they are about, as
// { field: [fix, ...] }, in the order the fields first appear.
export const getFixesByField = fixes =>
    fixes.reduce((byField, fix) => {
        const { field } = CLAIM_LIVE_CHECK_FIXES[fix];
        return { ...byField, [field]: [...(byField[field] || []), fix] };
    }, {});

// Scroll to the field `fix` is about and put the keyboard focus on it.
// Returns whether a field was found. A target that cannot take focus
// itself (a label) is made focusable so a keyboard or screen reader
// user lands there too.
export const focusFixField = (fix, root = document) => {
    const target = CLAIM_LIVE_CHECK_FIXES[fix].targets
        .map(selector => root.querySelector(selector))
        .find(Boolean);
    if (!target) {
        return false;
    }
    if (typeof target.scrollIntoView === 'function') {
        target.scrollIntoView({ block: 'center' });
    }
    if (target.tabIndex < 0) {
        target.setAttribute('tabindex', '-1');
    }
    target.focus({ preventScroll: true });
    return true;
};
