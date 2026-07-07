import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchClaimCampaigns,
    failFetchClaimCampaigns,
    completeFetchClaimCampaigns,
} from '../actions/claimCampaigns';

const initialState = Object.freeze({
    fetching: false,
    data: null,
    error: null,
});

export default createReducer(
    {
        [startFetchClaimCampaigns]: state =>
            update(state, {
                fetching: { $set: true },
                error: { $set: null },
            }),
        [failFetchClaimCampaigns]: (state, error) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: error },
            }),
        [completeFetchClaimCampaigns]: (state, data) =>
            update(state, {
                fetching: { $set: false },
                data: { $set: data },
            }),
    },
    initialState,
);
