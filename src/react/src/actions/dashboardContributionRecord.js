import { createAction } from 'redux-act';
import apiRequest from '../util/apiRequest';
import {
    makeGetModerationEvent,
    makeGetProductionLocationsForPotentialMatches,
    logErrorAndDispatchFailure,
} from '../util/util';

export const startFetchingSingleModerationEvent = createAction(
    'START_FETCHING_SINGLE_MODERATION_EVENT',
);
export const failFetchingSingleModerationEvent = createAction(
    'FAIL_FETCHING_SINGLE_MODERATION_EVENT',
);
export const completeFetchingSingleModerationEvent = createAction(
    'COMPLETE_FETCHING_SINGLE_MODERATION_EVENT',
);
export const startFetchingPotentialMatches = createAction(
    'START_FETCHING_POTENTIAL_MATCHES',
);
export const failFetchingPotentialMatches = createAction(
    'FAIL_FETCHING_POTENTIAL_MATCHES',
);
export const completeFetchingPotentialMatches = createAction(
    'COMPLETE_FETCHING_POTENTIAL_MATCHES',
);
export const cleanupContributionRecord = createAction(
    'CLEANUP_CONTRIBUTION_RECORD',
);

export function fetchSingleModerationEvent(moderationID) {
    return async dispatch => {
        dispatch(startFetchingSingleModerationEvent());

        return apiRequest
            .get(makeGetModerationEvent(moderationID))
            .then(({ data }) => {
                dispatch(completeFetchingSingleModerationEvent(data));
            })
            .catch(err => {
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation event',
                        failFetchingSingleModerationEvent,
                    ),
                );
            });
    };
}

export function fetchPotentialMatches(data) {
    return async dispatch => {
        dispatch(startFetchingPotentialMatches());

        const { productionLocationName, countryCode, address } = data;

        return apiRequest
            .get(
                makeGetProductionLocationsForPotentialMatches(
                    productionLocationName,
                    countryCode,
                    address,
                ),
            )
            .then(({ potentialMatches }) => {
                dispatch(completeFetchingPotentialMatches(potentialMatches));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching potential matches',
                        failFetchingPotentialMatches,
                    ),
                ),
            );
    };
}
