import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import {
    logErrorAndDispatchFailure,
    makeFacilityListCleaningURL,
    makeFacilityListCleaningStartURL,
    makeFacilityListCleaningDecisionsURL,
    makeFacilityListCleaningApplyURL,
} from '../util/util';

export const startFetchFacilityListCleaning = createAction(
    'START_FETCH_FACILITY_LIST_CLEANING',
);
export const failFetchFacilityListCleaning = createAction(
    'FAIL_FETCH_FACILITY_LIST_CLEANING',
);
export const completeFetchFacilityListCleaning = createAction(
    'COMPLETE_FETCH_FACILITY_LIST_CLEANING',
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

export function fetchFacilityListCleaning(listID, { silent = false } = {}) {
    return dispatch => {
        if (!silent) {
            dispatch(startFetchFacilityListCleaning());
        }

        return apiRequest
            .get(makeFacilityListCleaningURL(listID))
            .then(({ data }) => dispatch(completeFetchFacilityListCleaning(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching the automated checks for this list',
                        failFetchFacilityListCleaning,
                    ),
                ),
            );
    };
}

export function startFacilityListCleaningRun(listID) {
    return dispatch => {
        dispatch(startFetchFacilityListCleaning());

        return apiRequest
            .post(makeFacilityListCleaningStartURL(listID), {})
            .then(({ data }) => dispatch(completeFetchFacilityListCleaning(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented starting the automated checks',
                        failFetchFacilityListCleaning,
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

export function applyFacilityListCleaning(listID) {
    return dispatch => {
        dispatch(startApplyFacilityListCleaning());

        return apiRequest
            .post(makeFacilityListCleaningApplyURL(listID), {})
            .then(({ data }) => dispatch(completeApplyFacilityListCleaning(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented applying the changes to your list',
                        failApplyFacilityListCleaning,
                    ),
                ),
            );
    };
}
