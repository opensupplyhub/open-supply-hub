import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startClaimLiveCheck,
    failClaimLiveCheck,
    completeClaimLiveCheck,
    resetClaimLiveCheck,
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
});

const knownStatuses = Object.values(CLAIM_LIVE_CHECK_STATUSES);

// Only what this page knows how to show is kept: an unknown status
// reads as "not available" and an unknown fix key is dropped, so a
// vocabulary mismatch with the API can never put raw text on the page.
const readAnswer = data => {
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

    if (status === CLAIM_LIVE_CHECK_STATUSES.NOT_PASSED && fixes.length === 0) {
        return {
            status: CLAIM_LIVE_CHECK_STATUSES.UNAVAILABLE,
            fixes,
            checksLeft,
        };
    }
    return { status, fixes, checksLeft };
};

export default createReducer(
    {
        [startClaimLiveCheck]: (state, { claimID }) =>
            update(state, {
                claimID: { $set: claimID },
                status: { $set: null },
                fixes: { $set: [] },
                checksLeft: { $set: 0 },
            }),
        [completeClaimLiveCheck]: (state, { claimID, data }) => {
            if (claimID !== state.claimID) {
                return state;
            }
            const { status, fixes, checksLeft } = readAnswer(data);
            return update(state, {
                status: { $set: status },
                fixes: { $set: fixes },
                checksLeft: { $set: checksLeft },
            });
        },
        [failClaimLiveCheck]: (state, { claimID }) => {
            if (claimID !== state.claimID) {
                return state;
            }
            return update(state, {
                status: { $set: CLAIM_LIVE_CHECK_STATUSES.UNAVAILABLE },
                fixes: { $set: [] },
            });
        },
        [resetClaimLiveCheck]: () => initialState,
    },
    initialState,
);
