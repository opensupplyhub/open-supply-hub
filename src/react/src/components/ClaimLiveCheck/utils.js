import { makePendingClaimEditLink } from '../../util/util';
import {
    CHECK_AGAIN_QUERY_PARAM,
    CLAIM_LIVE_CHECK_FIXES,
    FIX_QUERY_PARAM,
} from './constants';

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
