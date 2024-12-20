import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchSingleProductionLocation,
    failFetchSingleProductionLocation,
    completeFetchSingleProductionLocation,
    resetSingleProductionLocation,
    startFetchProductionLocations,
    failFetchProductionLocations,
    completeFetchProductionLocations,
} from '../actions/contributeProductionLocation';

const initialState = Object.freeze({
    singleProductionLocation: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    productionLocations: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: true },
                    error: { $set: null },
                    data: { $set: null },
                },
            }),
        [failFetchSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [resetSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    $set: initialState.singleProductionLocation,
                },
            }),
        [startFetchProductionLocations]: state =>
            update(state, {
                productionLocations: {
                    fetching: { $set: true },
                    error: { $set: null },
                    data: { $set: null },
                },
            }),
        [failFetchProductionLocations]: (state, payload) =>
            update(state, {
                productionLocations: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchProductionLocations]: (state, payload) =>
            update(state, {
                productionLocations: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
    },
    initialState,
);
