import { createAction } from 'redux-act';
import {
    logErrorAndDispatchFailure,
    downloadModerationEventsXLSX,
    makeGetModerationEventsWithQueryString,
} from '../util/util';
import apiRequest from '../util/apiRequest';

export const startFetchingModerationEvents = createAction(
    'START_FETCHING_MODERATION_EVENTS',
);
export const failFetchingModerationEvents = createAction(
    'FAIL_FETCHING_MODERATION_EVENTS',
);
export const completeFetchingModerationEvents = createAction(
    'COMPLETE_FETCHING_MODERATION_EVENTS',
);
export const clearModerationEvents = createAction('CLEAR_MODERATION_EVENTS');
export const startDownloadingModerationEvents = createAction(
    'START_DOWNLOADING_MODERATION_EVENTS',
);
export const failDownloadingModerationEvents = createAction(
    'FAIL_DOWNLOADING_MODERATION_EVENTS',
);
export const completeDownloadingModerationEvents = createAction(
    'COMPLETE_DOWNLOADING_MODERATION_EVENTS',
);

export function fetchModerationEvents(
    page = 0,
    pageSize = 5,
    sortBy = 'created_at',
    orderBy = 'desc',
) {
    return async dispatch => {
        dispatch(startFetchingModerationEvents());

        return apiRequest
            .get(
                makeGetModerationEventsWithQueryString(
                    '',
                    page,
                    pageSize,
                    sortBy,
                    orderBy,
                ),
            )
            .then(({ data }) => {
                dispatch(completeFetchingModerationEvents(data));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation events',
                        failFetchingModerationEvents,
                    ),
                ),
            );
    };
}

export function downloadModerationEvents(data) {
    return dispatch => {
        dispatch(startDownloadingModerationEvents());

        try {
            downloadModerationEventsXLSX(data);
            dispatch(completeDownloadingModerationEvents());
        } catch (err) {
            dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented downloading moderation events',
                    failDownloadingModerationEvents,
                ),
            );
        }
    };
}
