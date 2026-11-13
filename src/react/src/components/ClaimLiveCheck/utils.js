import { makePendingClaimEditLink } from '../../util/util';
import {
    CHECKING_BAR_ANCHOR_MS,
    CHECKING_BAR_ANCHOR_PERCENT,
    CHECKING_BAR_MAX_PERCENT,
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

/**
 * How full the progress bar is, as a whole percentage. It follows the
 * time passed on a curve that slows as it goes and stops short of
 * full; only `done` (the result has arrived) fills it.
 */
export const getCheckingProgress = (elapsedMs, done) => {
    if (done) {
        return 100;
    }
    const rate =
        -Math.log(1 - CHECKING_BAR_ANCHOR_PERCENT / 100) /
        CHECKING_BAR_ANCHOR_MS;
    const percent = 100 * (1 - Math.exp(-rate * Math.max(0, elapsedMs)));
    return Math.min(CHECKING_BAR_MAX_PERCENT, Math.round(percent));
};

export const STEP_STATES = Object.freeze({
    DONE: 'done',
    NOW: 'now',
    WAITING: 'waiting',
});

/**
 * The state of each step in CHECKING_STEPS after `elapsedMs`. A step
 * is finished once the next one has started, so the last step is only
 * ever finished by `done`.
 */
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

/**
 * The facts to rotate through while the check runs. The fact about the
 * location is only included when the data the claim form already
 * loaded has both its name and how many organisations contributed to
 * it, which the public profile shows too.
 */
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

/**
 * How many organisations contributed to a production location, from
 * the public production location payload, or null when it does not
 * say.
 */
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

/**
 * The pending claim edit page, opened at the field `fix` is about.
 * `canCheckAgain` asks that page to run the check again after saving.
 */
export const makeFixLink = (claimID, fix, canCheckAgain) => {
    const params = new URLSearchParams();
    if (isKnownFix(fix)) {
        params.set(FIX_QUERY_PARAM, fix);
    }
    if (canCheckAgain) {
        params.set(CHECK_AGAIN_QUERY_PARAM, '1');
    }
    const query = params.toString();
    const link = makePendingClaimEditLink(encodeURIComponent(claimID));
    return query ? `${link}?${query}` : link;
};

/**
 * Read a "go back and fix it" choice from the edit page's query
 * string. The query string is user-editable, so `fix` is only ever one
 * of the preset keys (or null) and `checkAgain` is a plain boolean.
 */
export const parseFixParams = search => {
    const params = new URLSearchParams(search || '');
    const fix = params.get(FIX_QUERY_PARAM);
    return {
        fix: isKnownFix(fix) ? fix : null,
        checkAgain: params.get(CHECK_AGAIN_QUERY_PARAM) === '1',
    };
};

/**
 * Scroll to the field `fix` is about and put the keyboard focus on it.
 * Returns whether a field was found. Some targets cannot take focus
 * themselves (a label, a disabled input); those are made focusable so
 * a keyboard or screen reader user lands in the same place.
 */
export const focusFixField = (fix, root = document) => {
    if (!isKnownFix(fix)) {
        return false;
    }
    const target = CLAIM_LIVE_CHECK_FIXES[fix].targets
        .map(selector => root.querySelector(selector))
        .find(Boolean);
    if (!target) {
        return false;
    }
    if (typeof target.scrollIntoView === 'function') {
        target.scrollIntoView({ block: 'center' });
    }
    if (target.tabIndex < 0 || target.disabled) {
        target.setAttribute('tabindex', '-1');
    }
    target.focus({ preventScroll: true });
    return true;
};
