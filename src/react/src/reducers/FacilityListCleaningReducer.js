import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchFacilityListCleaning,
    failFetchFacilityListCleaning,
    completeFetchFacilityListCleaning,
    resetFacilityListCleaning,
    startSubmitFacilityListCleaningDecisions,
    failSubmitFacilityListCleaningDecisions,
    completeSubmitFacilityListCleaningDecisions,
    startApplyFacilityListCleaning,
    failApplyFacilityListCleaning,
    completeApplyFacilityListCleaning,
} from '../actions/facilityListCleaning';

import { completeSubmitLogOut } from '../actions/auth';

const initialState = Object.freeze({
    data: null,
    fetching: false,
    error: null,
    submitting: false,
    submitError: null,
    applying: false,
    applyError: null,
    lastApplied: null,
});

export default createReducer(
    {
        [startFetchFacilityListCleaning]: state =>
            update(state, {
                fetching: { $set: true },
                error: { $set: null },
            }),
        [failFetchFacilityListCleaning]: (state, payload) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: payload },
            }),
        [completeFetchFacilityListCleaning]: (state, payload) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: null },
                data: { $set: payload },
            }),
        [startSubmitFacilityListCleaningDecisions]: state =>
            update(state, {
                submitting: { $set: true },
                submitError: { $set: null },
            }),
        [failSubmitFacilityListCleaningDecisions]: (state, payload) =>
            update(state, {
                submitting: { $set: false },
                submitError: { $set: payload },
            }),
        [completeSubmitFacilityListCleaningDecisions]: (state, payload) =>
            update(state, {
                submitting: { $set: false },
                submitError: { $set: null },
                data: { $set: payload },
            }),
        [startApplyFacilityListCleaning]: state =>
            update(state, {
                applying: { $set: true },
                applyError: { $set: null },
            }),
        [failApplyFacilityListCleaning]: (state, payload) =>
            update(state, {
                applying: { $set: false },
                applyError: { $set: payload },
            }),
        [completeApplyFacilityListCleaning]: (state, payload) =>
            update(state, {
                applying: { $set: false },
                applyError: { $set: null },
                data: { $set: payload },
                lastApplied: { $set: payload.applied || null },
            }),
        [resetFacilityListCleaning]: () => initialState,
        [completeSubmitLogOut]: () => initialState,
    },
    initialState,
);
