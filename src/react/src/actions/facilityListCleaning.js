import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import {
    logErrorAndDispatchFailure,
    makeFacilityListCleaningURL,
    makeFacilityListCleaningStartURL,
    makeFacilityListCleaningDecisionsURL,
    makeFacilityListCleaningSubmitURL,
    makeFacilityListCleaningEventsURL,
} from '../util/util';

// A fetch names the list it is for, and its reply carries the mutation
// count (decisions and submissions sent or saved) as it stood when the
// request went out: the store drops a reply for another list, or one
// fetched before a later change, instead of overwriting newer rows.
export const startFetchFacilityListCleaning = createAction(
    'START_FETCH_FACILITY_LIST_CLEANING',
    ({ listID, silent = false, restart = false }) => ({
        listID,
        silent,
        restart,
    }),
);
export const failFetchFacilityListCleaning = createAction(
    'FAIL_FETCH_FACILITY_LIST_CLEANING',
    ({ listID, error }) => ({ listID, error }),
);
export const completeFetchFacilityListCleaning = createAction(
    'COMPLETE_FETCH_FACILITY_LIST_CLEANING',
    ({ listID, mutation, data }) => ({ listID, mutation, data }),
);
export const resetFacilityListCleaning = createAction(
    'RESET_FACILITY_LIST_CLEANING',
);

export const startSubmitFacilityListCleaningDecisions = createAction(
    'START_SUBMIT_FACILITY_LIST_CLEANING_DECISIONS',
);
export const failSubmitFacilityListCleaningDecisions = createAction(
    'FAIL_SUBMIT_FACILITY_LIST_CLEANING_DECISIONS',
);
export const completeSubmitFacilityListCleaningDecisions = createAction(
    'COMPLETE_SUBMIT_FACILITY_LIST_CLEANING_DECISIONS',
);

export const startApplyFacilityListCleaning = createAction(
    'START_APPLY_FACILITY_LIST_CLEANING',
);
export const failApplyFacilityListCleaning = createAction(
    'FAIL_APPLY_FACILITY_LIST_CLEANING',
);
export const completeApplyFacilityListCleaning = createAction(
    'COMPLETE_APPLY_FACILITY_LIST_CLEANING',
);

const mutationCount = getState =>
    (getState().facilityListCleaning || {}).mutation || 0;

export function fetchFacilityListCleaning(listID, { silent = false } = {}) {
    return (dispatch, getState) => {
        // A silent fetch (a poll, a refresh after the review) still says
        // which list it is for; it just shows no spinner.
        dispatch(startFetchFacilityListCleaning({ listID, silent }));
        const mutation = mutationCount(getState);

        return apiRequest
            .get(makeFacilityListCleaningURL(listID))
            .then(({ data }) =>
                dispatch(
                    completeFetchFacilityListCleaning({
                        listID,
                        mutation,
                        data,
                    }),
                ),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching the automated checks for this list',
                        error =>
                            failFetchFacilityListCleaning({ listID, error }),
                    ),
                ),
            );
    };
}

export function startFacilityListCleaningRun(listID) {
    return (dispatch, getState) => {
        // A restart replaces the run, so it counts as a change: a poll
        // sent before it cannot bring the old run back.
        dispatch(startFetchFacilityListCleaning({ listID, restart: true }));

        return apiRequest
            .post(makeFacilityListCleaningStartURL(listID), {})
            .then(({ data }) =>
                dispatch(
                    completeFetchFacilityListCleaning({
                        listID,
                        mutation: mutationCount(getState),
                        data,
                    }),
                ),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented starting the automated checks',
                        error =>
                            failFetchFacilityListCleaning({ listID, error }),
                    ),
                ),
            );
    };
}

export function submitFacilityListCleaningDecisions(listID, decisions) {
    return dispatch => {
        dispatch(startSubmitFacilityListCleaningDecisions());

        return apiRequest
            .post(makeFacilityListCleaningDecisionsURL(listID), { decisions })
            .then(({ data }) =>
                dispatch(completeSubmitFacilityListCleaningDecisions(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented saving your decision',
                        failSubmitFacilityListCleaningDecisions,
                    ),
                ),
            );
    };
}

// v3: the one submission. Applies every accepted change (or none, with
// asUploaded) and closes the review window for good.
export function applyFacilityListCleaning(listID, { asUploaded = false } = {}) {
    return dispatch => {
        dispatch(startApplyFacilityListCleaning());

        return apiRequest
            .post(makeFacilityListCleaningSubmitURL(listID), {
                as_uploaded: asUploaded,
            })
            .then(({ data }) =>
                dispatch(completeApplyFacilityListCleaning(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented submitting your list',
                        failApplyFacilityListCleaning,
                    ),
                ),
            );
    };
}

export function submitFacilityListCleaningGroupDecisions(listID, groups) {
    return dispatch => {
        dispatch(startSubmitFacilityListCleaningDecisions());

        return apiRequest
            .post(makeFacilityListCleaningDecisionsURL(listID), { groups })
            .then(({ data }) =>
                dispatch(completeSubmitFacilityListCleaningDecisions(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented saving your decisions',
                        failSubmitFacilityListCleaningDecisions,
                    ),
                ),
            );
    };
}

// Metrics for "submit versus click away": fire-and-forget, never shown.
export function recordFacilityListCleaningEvent(listID, kind, meta = {}) {
    return apiRequest
        .post(makeFacilityListCleaningEventsURL(listID), { kind, meta })
        .catch(() => null);
}

// Same, for the moment the tab is closing: fetch with keepalive survives
// page unload where an XHR would be cancelled.
export function beaconFacilityListCleaningEvent(listID, kind, meta = {}) {
    try {
        fetch(makeFacilityListCleaningEventsURL(listID), {
            method: 'POST',
            keepalive: true,
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-OAR-Client-Key': window.ENVIRONMENT.OAR_CLIENT_KEY,
            },
            body: JSON.stringify({ kind, meta }),
        }).catch(() => null);
    } catch (e) {
        // best effort only
    }
}
