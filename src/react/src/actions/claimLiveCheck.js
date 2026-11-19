import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import { makeClaimLiveCheckURL } from '../util/util';

// The live check of a just-submitted claim (OSDEV-3805). Starting a
// check is a POST that returns at once; the page then polls with GET
// until the check has an answer.
export const startClaimLiveCheck = createAction('START_CLAIM_LIVE_CHECK');
export const failClaimLiveCheck = createAction('FAIL_CLAIM_LIVE_CHECK');
export const completeClaimLiveCheck = createAction('COMPLETE_CLAIM_LIVE_CHECK');
export const resetClaimLiveCheck = createAction('RESET_CLAIM_LIVE_CHECK');

// Every action carries the claim id it was sent for, so the reducer can
// drop an answer that arrives after the page has moved on to another
// claim or has been left.
const request = (claimID, send) => dispatch =>
    send(makeClaimLiveCheckURL(claimID))
        .then(({ data }) => dispatch(completeClaimLiveCheck({ claimID, data })))
        // The check is advisory and the claim is already submitted, so
        // a failed request is shown as "not available", never as an
        // error the claimant has to deal with.
        .catch(() => dispatch(failClaimLiveCheck({ claimID })));

export function runClaimLiveCheck(claimID) {
    return dispatch => {
        dispatch(startClaimLiveCheck({ claimID }));
        return dispatch(request(claimID, url => apiRequest.post(url)));
    };
}

// The page has waited its minute and is showing "not available". Tell
// the API, so a result that arrives from now on is emailed to the
// claimant rather than assumed to have been seen.
export function giveUpClaimLiveCheck(claimID) {
    return request(claimID, url => apiRequest.post(url, { timed_out: true }));
}

// The pending claim edit page reads the claim's latest check when it
// opens, to mark the fields that still need a change. The API returns
// no fixes once the claim has been edited since that check.
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

export function fetchClaimLiveCheckFixes(claimID) {
    return dispatch => {
        dispatch(startFetchClaimLiveCheckFixes({ claimID }));
        return (
            apiRequest
                .get(makeClaimLiveCheckURL(claimID))
                .then(({ data }) =>
                    dispatch(
                        completeFetchClaimLiveCheckFixes({ claimID, data }),
                    ),
                )
                // Advisory, like the check itself: without an answer
                // the edit page is simply shown as it always has been.
                .catch(() =>
                    dispatch(failFetchClaimLiveCheckFixes({ claimID })),
                )
        );
    };
}

export function pollClaimLiveCheck(claimID) {
    return request(claimID, url => apiRequest.get(url));
}
