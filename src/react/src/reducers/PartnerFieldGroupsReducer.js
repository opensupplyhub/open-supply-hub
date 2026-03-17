import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchPartnerFieldGroups,
    failFetchPartnerFieldGroups,
    completeFetchPartnerFieldGroups,
} from '../actions/partnerFieldGroups';

const initialState = Object.freeze({
    fetching: false,
    data: null,
    error: null,
});

export default createReducer(
    {
        [startFetchPartnerFieldGroups]: state =>
            update(state, {
                fetching: { $set: true },
                error: { $set: null },
            }),
        [failFetchPartnerFieldGroups]: (state, error) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: error },
            }),
        [completeFetchPartnerFieldGroups]: (state, data) =>
            Object.freeze(
                update(state, {
                    fetching: { $set: false },
                    data: { $set: data },
                }),
            ),
    },
    initialState,
);
