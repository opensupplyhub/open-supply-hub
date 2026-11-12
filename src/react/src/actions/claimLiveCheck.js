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

export function pollClaimLiveCheck(claimID) {
    return request(claimID, url => apiRequest.get(url));
}
