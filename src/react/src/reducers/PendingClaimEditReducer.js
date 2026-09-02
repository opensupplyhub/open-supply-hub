/* eslint-disable camelcase */
import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchPendingClaim,
    failFetchPendingClaim,
    completeFetchPendingClaim,
    updatePendingClaimFormField,
    startSavePendingClaim,
    failSavePendingClaim,
    completeSavePendingClaim,
    startDeletePendingClaimAttachment,
    failDeletePendingClaimAttachment,
    completeDeletePendingClaimAttachment,
    resetPendingClaimEdit,
} from '../actions/pendingClaimEdit';

const initialState = Object.freeze({
    // The GET /pending/ payload — attachments live here.
    data: null,
    fetching: false,
    error: null,
    // camelCase form values driving the reused claim-form steps.
    formData: null,
    saving: false,
    savingError: null,
    // True right after a successful save; drives the outcome dialog.
    saved: false,
    deletingAttachment: false,
});

export default createReducer(
    {
        [startFetchPendingClaim]: state =>
            update(state, {
                fetching: { $set: true },
                error: { $set: null },
            }),
        [failFetchPendingClaim]: (state, error) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: error },
            }),
        [completeFetchPendingClaim]: (state, { data, formData }) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: null },
                data: { $set: data },
                formData: { $set: formData },
            }),
        // Deliberately does NOT clear `saved`: the reused claim-form
        // steps dispatch programmatic field updates from effects (e.g.
        // right after the post-save formik reinitialization), which
        // would close the outcome dialog in the same frame it opened.
        // `saved` is cleared when the next save starts, and on reset.
        [updatePendingClaimFormField]: (state, { field, value }) =>
            update(state, {
                formData: { [field]: { $set: value } },
                savingError: { $set: null },
            }),
        [startSavePendingClaim]: state =>
            update(state, {
                saving: { $set: true },
                savingError: { $set: null },
                saved: { $set: false },
            }),
        [failSavePendingClaim]: (state, error) =>
            update(state, {
                saving: { $set: false },
                savingError: { $set: error },
            }),
        [completeSavePendingClaim]: (state, { data, formData }) =>
            update(state, {
                saving: { $set: false },
                savingError: { $set: null },
                saved: { $set: true },
                data: { $set: data },
                formData: { $set: formData },
            }),
        [startDeletePendingClaimAttachment]: state =>
            update(state, {
                deletingAttachment: { $set: true },
                savingError: { $set: null },
            }),
        [failDeletePendingClaimAttachment]: (state, error) =>
            update(state, {
                deletingAttachment: { $set: false },
                savingError: { $set: error },
            }),
        [completeDeletePendingClaimAttachment]: (state, { data }) =>
            update(state, {
                deletingAttachment: { $set: false },
                data: { $set: data },
            }),
        [resetPendingClaimEdit]: () => initialState,
    },
    initialState,
);
