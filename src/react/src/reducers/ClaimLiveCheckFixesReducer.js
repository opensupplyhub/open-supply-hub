import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchClaimLiveCheckFixes,
    failFetchClaimLiveCheckFixes,
    completeFetchClaimLiveCheckFixes,
    resetClaimLiveCheckFixes,
} from '../actions/claimLiveCheck';
import { readAnswer } from './ClaimLiveCheckReducer';
import { CLAIM_LIVE_CHECK_STATUSES } from '../components/ClaimLiveCheck/constants';

// What the pending claim edit page marks (OSDEV-3805): the fixes of
// the claim's latest live check, while they are still current.
const initialState = Object.freeze({
    // The claim the fixes are for. Answers for any other are dropped.
    claimID: null,
    fetching: false,
    // Keys of the preset fixes. Empty unless the check did not pass.
    fixes: Object.freeze([]),
    checksLeft: 0,
});

export default createReducer(
    {
        [startFetchClaimLiveCheckFixes]: (state, { claimID }) =>
            update(state, {
                claimID: { $set: claimID },
                fetching: { $set: true },
                fixes: { $set: [] },
                checksLeft: { $set: 0 },
            }),
        [completeFetchClaimLiveCheckFixes]: (state, { claimID, data }) => {
            if (claimID !== state.claimID) {
                return state;
            }
            // Only the preset keys this page knows are kept, and only
            // for a check that did not pass.
            const { status, fixes, checksLeft } = readAnswer(data);
            const notPassed = status === CLAIM_LIVE_CHECK_STATUSES.NOT_PASSED;
            return update(state, {
                fetching: { $set: false },
                fixes: { $set: notPassed ? fixes : [] },
                checksLeft: { $set: checksLeft },
            });
        },
        [failFetchClaimLiveCheckFixes]: (state, { claimID }) => {
            if (claimID !== state.claimID) {
                return state;
            }
            return update(state, { fetching: { $set: false } });
        },
        [resetClaimLiveCheckFixes]: () => initialState,
    },
    initialState,
);
