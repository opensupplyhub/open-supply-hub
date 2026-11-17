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

// A decision reply carries the run, summary and groups in full but only
// the rows it changed (rows_partial), so one click on a long list does
// not send every row back. Those rows replace their earlier versions;
// anything only the full read carries (tour_seen, enabled) is kept.
const mergeDecisions = (data, payload) => {
    if (!payload || !payload.rows_partial) return payload;
    const { rows_partial: omit, ...rest } = payload;
    const changed = new Map((payload.rows || []).map(r => [r.row_number, r]));
    const existing = (data && data.rows) || [];
    const known = new Set(existing.map(r => r.row_number));
    const rows = existing
        .map(r => changed.get(r.row_number) || r)
        .concat((payload.rows || []).filter(r => !known.has(r.row_number)))
        .sort((a, b) => a.row_number - b.row_number);
    return { ...(data || {}), ...rest, rows };
};

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
                data: { $set: mergeDecisions(state.data, payload) },
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
