import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import { makeClaimLiveCheckURL } from '../util/util';

// Starting a check is a POST that returns at once; the page then polls
// with GET until the check has an answer.
export const startClaimLiveCheck = createAction('START_CLAIM_LIVE_CHECK');
export const failClaimLiveCheck = createAction('FAIL_CLAIM_LIVE_CHECK');
export const completeClaimLiveCheck = createAction('COMPLETE_CLAIM_LIVE_CHECK');
export const resetClaimLiveCheck = createAction('RESET_CLAIM_LIVE_CHECK');

// The pending claim edit page reads the claim's latest check when it
// opens, to mark the fields that still need a change.
export const startFetchClaimLiveCheckFixes = createAction(
    'START_FETCH_CLAIM_LIVE_CHECK_FIXES',
);
export const failFetchClaimLiveCheckFixes = createAction(
    'FAIL_FETCH_CLAIM_LIVE_CHECK_FIXES',
);
export const completeFetchClaimLiveCheckFixes = createAction(
    'COMPLETE_FETCH_CLAIM_LIVE_CHECK_FIXES',
);
export const resetClaimLiveCheckFixes = createAction(
    'RESET_CLAIM_LIVE_CHECK_FIXES',
);

// Every action carries the claim id it was sent for, so the reducer can
// drop an answer that arrives after the page has moved on. The check is
// advisory, so a failed request is never shown as an error.
const request = (
    claimID,
    send,
    [complete, fail] = [completeClaimLiveCheck, failClaimLiveCheck],
) => dispatch =>
    send(makeClaimLiveCheckURL(claimID))
        .then(({ data }) => dispatch(complete({ claimID, data })))
        .catch(() => dispatch(fail({ claimID })));

export function runClaimLiveCheck(claimID) {
    return dispatch => {
        dispatch(startClaimLiveCheck({ claimID }));
        return dispatch(request(claimID, url => apiRequest.post(url)));
    };
}

// Tells the API the page has stopped waiting, so a result that arrives
// from now on is emailed to the claimant.
export function giveUpClaimLiveCheck(claimID) {
    return request(claimID, url => apiRequest.post(url, { timed_out: true }));
}

export function fetchClaimLiveCheckFixes(claimID) {
    return dispatch => {
        dispatch(startFetchClaimLiveCheckFixes({ claimID }));
        return dispatch(
            request(claimID, url => apiRequest.get(url), [
                completeFetchClaimLiveCheckFixes,
                failFetchClaimLiveCheckFixes,
            ]),
        );
    };
}

export function pollClaimLiveCheck(claimID) {
    return request(claimID, url => apiRequest.get(url));
}
