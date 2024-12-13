import { createAction } from 'redux-act';
import apiRequest from '../util/apiRequest';
import {
    makeModerationEventRecordURL,
    makeGetProductionLocationsForPotentialMatches,
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
export const startUpdateModerationEventRecord = createAction(
    'START_UPDATE_MODERATION_EVENT',
);
export const completeUpdateModerationEventRecord = createAction(
    'COMPLETE_UPDATE_MODERATION_EVENT',
);
export const failUpdateModerationEventRecord = createAction(
    'FAIL_UPDATE_MODERATION_EVENT',
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

export function updateModerationEvent(moderationID) {
    return async dispatch => {
        dispatch(startUpdateModerationEventRecord());

        return apiRequest
            .patch(makeModerationEventRecordURL(moderationID))
            .then(data => {
                dispatch(completeUpdateModerationEventRecord(data));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented updating moderation event record',
                        failUpdateModerationEventRecord,
                    ),
                ),
            );
    };
}
