import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchCountryOptions,
    completeFetchCountryOptions,
    failFetchCountryOptions,
} from '../actions/filterOptions';
import {
    updateFacilityTypeFilter,
    updateProcessingTypeFilter,
} from '../actions/filters';

const initialState = Object.freeze({
    countries: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    processingTypeOptions: Object.freeze({
        data: [],
        fetching: false,
        error: null,
    }),
    processingType: Object.freeze({
        data: [],
        fetching: false,
        error: null,
    }),
    locationType: Object.freeze({
        data: [],
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchCountryOptions]: state =>
            update(state, {
                countries: {
                    data: {
                        $set: initialState.countries.data,
                    },
                    fetching: { $set: true },
                    error: { $set: initialState.countries.error },
                },
            }),
        [completeFetchCountryOptions]: (state, payload) =>
            update(state, {
                countries: {
                    data: { $set: payload },
                    fetching: { $set: false },
                    error: { $set: initialState.countries.error },
                },
            }),
        [failFetchCountryOptions]: (state, error) =>
            update(state, {
                countries: {
                    fetching: { $set: false },
                    error: { $set: error },
                },
            }),
        [updateFacilityTypeFilter]: (state, payload) =>
            update(state, {
                locationType: { $set: payload },
            }),
        [updateProcessingTypeFilter]: (state, payload) =>
            update(state, {
                processingType: { $set: payload },
            }),
    },
    initialState,
);
