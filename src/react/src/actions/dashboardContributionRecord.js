import { createAction } from 'redux-act';
import apiRequest from '../util/apiRequest';
import {
    makeModerationEventRecordURL,
    makeGetProductionLocationsForPotentialMatches,
    makeProductionLocationFromModerationEventURL,
    logErrorAndDispatchFailure,
} from '../util/util';

export const startFetchSingleModerationEvent = createAction(
    'START_FETCH_SINGLE_MODERATION_EVENT',
);
export const failFetchSingleModerationEvent = createAction(
    'FAIL_FETCH_SINGLE_MODERATION_EVENT',
);
export const completeFetchSingleModerationEvent = createAction(
    'COMPLETE_FETCH_SINGLE_MODERATION_EVENT',
);
export const startFetchPotentialMatches = createAction(
    'START_FETCH_POTENTIAL_MATCHES',
);
export const failFetchPotentialMatches = createAction(
    'FAIL_FETCH_POTENTIAL_MATCHES',
);
export const completeFetchPotentialMatches = createAction(
    'COMPLETE_FETCH_POTENTIAL_MATCHES',
);
export const cleanupContributionRecord = createAction(
    'CLEANUP_CONTRIBUTION_RECORD',
);
export const startUpdateSingleModerationEvent = createAction(
    'START_UPDATE_SINGLE_MODERATION_EVENT',
);
export const completeUpdateSingleModerationEvent = createAction(
    'COMPLETE_UPDATE_SINGLE_MODERATION_EVENT',
);
export const failUpdateSingleModerationEvent = createAction(
    'FAIL_UPDATE_SINGLE_MODERATION_EVENT',
);
export const startCreateProductionLocationFromModerationEvent = createAction(
    'START_CREATE_PRODUCTION_LOCATION_FROM_MODERATION_EVENT',
);
export const completeCreateProductionLocationFromModerationEvent = createAction(
    'COMPLETE_CREATE_PRODUCTION_LOCATION_FROM_MODERATION_EVENT',
);
export const failCreateProductionLocationFromModerationEvent = createAction(
    'FAIL_CREATE_PRODUCTION_LOCATION_FROM_MODERATION_EVENT',
);

export function fetchSingleModerationEvent(moderationID) {
    return async dispatch => {
        dispatch(startFetchSingleModerationEvent());

        return apiRequest
            .get(makeModerationEventRecordURL(moderationID))
            .then(({ data }) => {
                dispatch(completeFetchSingleModerationEvent(data));
            })
            .catch(err => {
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation event',
                        failFetchSingleModerationEvent,
                    ),
                );
            });
    };
}

export function fetchPotentialMatches(data) {
    return async dispatch => {
        dispatch(startFetchPotentialMatches());

        const {
            productionLocationName,
            countryCode,
            productionLocationAddress,
        } = data;

        return apiRequest
            .get(
                makeGetProductionLocationsForPotentialMatches(
                    productionLocationName,
                    countryCode,
                    productionLocationAddress,
                ),
            )
            .then(potentialMatches => {
                if (potentialMatches.data) {
                    dispatch(
                        completeFetchPotentialMatches(potentialMatches.data),
                    );
                }
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching potential matches',
                        failFetchPotentialMatches,
                    ),
                ),
            );
    };
}

export function updateSingleModerationEvent(moderationID, status) {
    return async dispatch => {
        dispatch(startUpdateSingleModerationEvent());

        return apiRequest
            .patch(makeModerationEventRecordURL(moderationID), { status })
            .then(({ data }) => {
                dispatch(completeUpdateSingleModerationEvent(data));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented updating moderation event record',
                        failUpdateSingleModerationEvent,
                    ),
                ),
            );
    };
}

// TODO: Refactor actions. You always invoke fetch of moderation events
// See this as a reference: src/react/src/actions/dashboardActivityReports.js
// There will be a separate actions but with the same purpose of updating Redux State.
export function createProductionLocationFromModerationEvent(moderationID) {
    return async dispatch => {
        dispatch(startCreateProductionLocationFromModerationEvent());

        return apiRequest
            .post(makeProductionLocationFromModerationEventURL(moderationID))
            .then(({ data }) => {
                dispatch(
                    completeCreateProductionLocationFromModerationEvent(data),
                );
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented creating production location from moderation event record',
                        failCreateProductionLocationFromModerationEvent,
                    ),
                ),
            );
    };
}
