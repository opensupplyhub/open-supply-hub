import { createReducer } from 'redux-act';
import update from 'immutability-helper';
import constant from 'lodash/constant';
import get from 'lodash/get';
import reject from 'lodash/reject';
import find from 'lodash/find';

import {
    startFetchFacilityToAdjust,
    failFetchFacilityToAdjust,
    completeFetchFacilityToAdjust,
    clearFacilityToAdjust,
    resetAdjustFacilityState,
    updateFacilityToAdjustOSID,
    startSplitFacilityMatch,
    failSplitFacilityMatch,
    completeSplitFacilityMatch,
} from '../actions/splitOrPromoteFacilityMatches';

const initialState = Object.freeze({
    facility: Object.freeze({
        osID: '',
        data: null,
        fetching: false,
        error: null,
    }),
    adjustFacilities: Object.freeze({
        data: Object.freeze([]),
        fetching: false,
        error: null,
    }),
});

const handleCompleteSplitFacilityMatch = (state, data) => {
    const existingMatches = get(state, 'facility.data.properties.matches', []);

    const matchIDFromData = get(data, 'match_id', null);

    const {
        list_contributor_id = null, // eslint-disable-line camelcase
        // eslint-disable-next-line camelcase
    } = find(existingMatches, ({ match_id }) => match_id === matchIDFromData);

    return update(state, {
        adjustFacilities: {
            data: { $set: state.adjustFacilities.data.concat(data) },
            fetching: { $set: initialState.adjustFacilities.fetching },
        },
        facility: {
            data: {
                properties: {
                    contributors: {
                        $set: reject(
                            state.facility.data.properties.contributors,
                            { id: list_contributor_id },
                        ),
                    },
                },
            },
        },
    });
};

export default createReducer(
    {
        [startFetchFacilityToAdjust]: state =>
            update(state, {
                facility: {
                    fetching: { $set: true },
                    error: { $set: initialState.facility.error },
                },
            }),
        [failFetchFacilityToAdjust]: (state, error) =>
            update(state, {
                facility: {
                    fetching: { $set: initialState.facility.fetching },
                    error: { $set: error },
                },
            }),
        [completeFetchFacilityToAdjust]: (state, data) =>
            update(state, {
                facility: {
                    data: { $set: data },
                    fetching: { $set: initialState.facility.fetching },
                },
            }),
        [updateFacilityToAdjustOSID]: (state, osID) =>
            update(state, {
                facility: {
                    osID: { $set: osID },
                    error: { $set: initialState.facility.error },
                },
            }),
        [clearFacilityToAdjust]: state =>
            update(state, {
                facility: {
                    $set: initialState.facility,
                },
            }),
        [startSplitFacilityMatch]: state =>
            update(state, {
                splitOrPromoteFacilities: {
                    fetching: { $set: true },
                    error: {
                        $set: initialState.splitOrPromoteFacilities.error,
                    },
                },
            }),
        [failSplitFacilityMatch]: (state, error) =>
            update(state, {
                splitOrPromoteFacilities: {
                    fetching: {
                        $set: initialState.splitOrPromoteFacilities.fetching,
                    },
                    error: { $set: error },
                },
            }),
        [completeSplitFacilityMatch]: handleCompleteSplitFacilityMatch,
        [resetAdjustFacilityState]: constant(initialState),
    },
    initialState,
);
