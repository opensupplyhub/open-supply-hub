import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchingSingleProductionLocation,
    failFetchingSingleProductionLocation,
    completeFetchingSingleProductionLocation,
} from '../actions/contributeProductionLocation';

const initialState = Object.freeze({
    singleProductionLocation: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchingSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: true },
                    error: { $set: null },
                    data: { $set: null },
                },
            }),
        [failFetchingSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchingSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
    },
    initialState,
);
