import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    saveSearchParameters,
    clearSearchParameters,
} from '../actions/searchParameters';

const initialState = Object.freeze({
    name: null,
    address: false,
    country: null,
});

export default createReducer(
    {
        [saveSearchParameters]: (state, payload) =>
            update(state, { $merge: payload }),
        [clearSearchParameters]: () => initialState,
    },
    initialState,
);
