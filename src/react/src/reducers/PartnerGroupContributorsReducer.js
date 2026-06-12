import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchPartnerGroupContributors,
    failFetchPartnerGroupContributors,
    completeFetchPartnerGroupContributors,
} from '../actions/partnerGroupContributors';

const initialState = Object.freeze({
    fetching: false,
    data: null,
    error: null,
});

export default createReducer(
    {
        [startFetchPartnerGroupContributors]: state =>
            update(state, {
                fetching: { $set: true },
                error: { $set: null },
            }),
        [failFetchPartnerGroupContributors]: (state, error) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: error },
            }),
        [completeFetchPartnerGroupContributors]: (state, data) =>
            Object.freeze(
                update(state, {
                    fetching: { $set: false },
                    data: { $set: data },
                }),
            ),
    },
    initialState,
);
