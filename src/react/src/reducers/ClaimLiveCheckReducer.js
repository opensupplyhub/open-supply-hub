import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startClaimLiveCheck,
    failClaimLiveCheck,
    completeClaimLiveCheck,
    resetClaimLiveCheck,
    startFetchClaimLiveCheckFixes,
    failFetchClaimLiveCheckFixes,
    completeFetchClaimLiveCheckFixes,
    resetClaimLiveCheckFixes,
} from '../actions/claimLiveCheck';
import {
    CLAIM_LIVE_CHECK_FIXES,
    CLAIM_LIVE_CHECK_STATUSES,
} from '../components/ClaimLiveCheck/constants';

const initialState = Object.freeze({
    // The claim being checked. Answers for any other claim are dropped.
    claimID: null,
    // One of CLAIM_LIVE_CHECK_STATUSES, or null before the first answer.
    status: null,
    // Keys of the preset fixes to show when the claim did not pass.
    fixes: Object.freeze([]),
    checksLeft: 0,
    // True when the check ended without a result and none is coming,
    // so the claimant must not be told to expect one by email.
    noResult: false,
});

const knownStatuses = Object.values(CLAIM_LIVE_CHECK_STATUSES);

// Only what the page knows how to show is kept: an unknown status
// reads as "not available" and an unknown fix key is dropped.
export const readAnswer = data => {
    const status = knownStatuses.includes(data?.status)
        ? data.status
        : CLAIM_LIVE_CHECK_STATUSES.UNAVAILABLE;
    const fixes = Array.isArray(data?.fixes)
        ? data.fixes.filter(fix =>
              Object.prototype.hasOwnProperty.call(CLAIM_LIVE_CHECK_FIXES, fix),
          )
        : [];
    const checksLeft = Number.isInteger(data?.checks_left)
        ? data.checks_left
        : 0;
    // Only an unavailable check can be one that ended without a result.
    const noResult =
        status === CLAIM_LIVE_CHECK_STATUSES.UNAVAILABLE &&
        data?.no_result === true;

    if (status === CLAIM_LIVE_CHECK_STATUSES.NOT_PASSED && fixes.length === 0) {
        return {
            status: CLAIM_LIVE_CHECK_STATUSES.UNAVAILABLE,
            fixes,
            checksLeft,
            noResult: false,
        };
    }
    return { status, fixes, checksLeft, noResult };
};

const makeLiveCheckReducer = (start, fail, complete, reset) =>
    createReducer(
        {
            [start]: (state, { claimID }) =>
                update(state, {
                    claimID: { $set: claimID },
                    status: { $set: null },
                    fixes: { $set: [] },
                    checksLeft: { $set: 0 },
                    noResult: { $set: false },
                }),
            [complete]: (state, { claimID, data }) => {
                if (claimID !== state.claimID) {
                    return state;
                }
                const { status, fixes, checksLeft, noResult } = readAnswer(
                    data,
                );
                return update(state, {
                    status: { $set: status },
                    fixes: { $set: fixes },
                    checksLeft: { $set: checksLeft },
                    noResult: { $set: noResult },
                });
            },
            [fail]: (state, { claimID }) => {
                if (claimID !== state.claimID) {
                    return state;
                }
                return update(state, {
                    status: { $set: CLAIM_LIVE_CHECK_STATUSES.UNAVAILABLE },
                    fixes: { $set: [] },
                    noResult: { $set: false },
                });
            },
            [reset]: () => initialState,
        },
        initialState,
    );

// The claim's latest check, as read by the pending claim edit page.
export const claimLiveCheckFixesReducer = makeLiveCheckReducer(
    startFetchClaimLiveCheckFixes,
    failFetchClaimLiveCheckFixes,
    completeFetchClaimLiveCheckFixes,
    resetClaimLiveCheckFixes,
);

export default makeLiveCheckReducer(
    startClaimLiveCheck,
    failClaimLiveCheck,
    completeClaimLiveCheck,
    resetClaimLiveCheck,
);
