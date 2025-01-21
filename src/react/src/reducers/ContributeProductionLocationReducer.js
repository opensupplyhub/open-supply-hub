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
    resetProductionLocations,
} from '../actions/contributeProductionLocation';

const initialState = Object.freeze({
    singleProductionLocation: Object.freeze({
        data: {},
        fetching: false,
        error: null,
    }),
    productionLocations: Object.freeze({
        data: [],
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        // Single Production Location
        [startFetchSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: true },
                    error: {
                        $set: initialState.singleProductionLocation.error,
                    },
                    data: { $set: initialState.singleProductionLocation.data },
                },
            }),
        [failFetchSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: {
                        $set: initialState.singleProductionLocation.fetching,
                    },
                    error: { $set: payload },
                },
            }),
        [completeFetchSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: {
                        $set: initialState.singleProductionLocation.fetching,
                    },
                    error: {
                        $set: initialState.singleProductionLocation.error,
                    },
                    data: { $set: payload },
                },
            }),
        [resetSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    $set: initialState.singleProductionLocation,
                },
            }),

        // Production Locations
        [startFetchProductionLocations]: state =>
            update(state, {
                productionLocations: {
                    fetching: { $set: true },
                    error: { $set: initialState.productionLocations.error },
                    data: { $set: initialState.productionLocations.data },
                },
            }),
        [failFetchProductionLocations]: (state, payload) =>
            update(state, {
                productionLocations: {
                    fetching: {
                        $set: initialState.productionLocations.fetching,
                    },
                    error: { $set: payload },
                },
            }),
        [completeFetchProductionLocations]: (state, payload) =>
            update(state, {
                productionLocations: {
                    fetching: {
                        $set: initialState.productionLocations.fetching,
                    },
                    error: { $set: initialState.productionLocations.error },
                    data: { $set: payload.data },
                },
            }),
        [resetProductionLocations]: state =>
            update(state, {
                productionLocations: {
                    $set: initialState.productionLocations,
                },
            }),
    },
    initialState,
);
