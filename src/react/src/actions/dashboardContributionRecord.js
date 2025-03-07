import { createAction } from 'redux-act';
import apiRequest from '../util/apiRequest';
import {
    makeModerationEventRecordURL,
    makeGetProductionLocationsForPotentialMatches,
    makeProductionLocationFromModerationEventURL,
    logErrorAndDispatchFailure,
} from '../util/util';
import { MODERATION_STATUSES_ENUM } from '../util/constants';

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
    // We need to explicitly update the status for proper UI handling
    // The status property doesn't exist in 'POST /v1/moderation-events/{moderation_id}/production-locations/' response
    payload => ({
        ...payload,
        status: MODERATION_STATUSES_ENUM.APPROVED,
    }),
);
export const failCreateProductionLocationFromModerationEvent = createAction(
    'FAIL_CREATE_PRODUCTION_LOCATION_FROM_MODERATION_EVENT',
);
export const startConfirmPotentialMatchFromModerationEvent = createAction(
    'START_CONFIRM_POTENTIAL_MATCH_FROM_MODERATION_EVENT',
);
export const completeConfirmPotentialMatchFromModerationEvent = createAction(
    'COMPLETE_CONFIRM_POTENTIAL_MATCH_FROM_MODERATION_EVENT',
    // We need to explicitly update the status for proper UI handling
    // The status property doesn't exist in 'PATCH /v1/moderation-events/{moderation_id}/production-locations/{os_id}/' response
    payload => ({
        ...payload,
        status: MODERATION_STATUSES_ENUM.APPROVED,
    }),
);
export const failConfirmPotentialMatchFromModerationEvent = createAction(
    'FAIL_CONFIRM_POTENTIAL_MATCH_FROM_MODERATION_EVENT',
);

export function fetchSingleModerationEvent(moderationID) {
    return dispatch => {
        if (!moderationID) {
            return null;
        }
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
    return dispatch => {
        dispatch(startFetchPotentialMatches());

        const {
            productionLocationName,
            productionLocationAddress,
            countryCode,
        } = data;

        return apiRequest
            .get(
                makeGetProductionLocationsForPotentialMatches(
                    productionLocationName,
                    productionLocationAddress,
                    countryCode,
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

export function updateSingleModerationEvent(
    moderationID,
    status,
    textCleaned,
    textRaw,
) {
    return dispatch => {
        if (!moderationID) {
            return null;
        }
        dispatch(startUpdateSingleModerationEvent());

        return apiRequest
            .patch(makeModerationEventRecordURL(moderationID), {
                status,
                action_reason_text_cleaned: textCleaned,
                action_reason_text_raw: textRaw,
            })
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

export function createProductionLocationFromModerationEvent(moderationID) {
    return dispatch => {
        if (!moderationID) {
            return null;
        }
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

export function confirmPotentialMatchFromModerationEvent(moderationID, osID) {
    return dispatch => {
        if (!moderationID) {
            return null;
        }
        dispatch(startConfirmPotentialMatchFromModerationEvent());

        return apiRequest
            .patch(
                makeProductionLocationFromModerationEventURL(
                    moderationID,
                    osID,
                ),
            )
            .then(({ data }) => {
                dispatch(
                    completeConfirmPotentialMatchFromModerationEvent(data),
                );
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented confirming potential match from moderation event record',
                        failConfirmPotentialMatchFromModerationEvent,
                    ),
                ),
            );
    };
}
