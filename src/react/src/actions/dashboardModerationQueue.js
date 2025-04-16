import { createAction } from 'redux-act';
import {
    logErrorAndDispatchFailure,
    downloadModerationEventsXLSX,
    makeGetModerationEventsWithQueryString,
    createQueryStringFromModerationQueueFilters,
} from '../util/util';
import apiRequest from '../util/apiRequest';

export const startFetchModerationEvents = createAction(
    'START_FETCH_MODERATION_EVENTS',
);
export const failFetchModerationEvents = createAction(
    'FAIL_FETCH_MODERATION_EVENTS',
);
export const completeFetchModerationEvents = createAction(
    'COMPLETE_FETCH_MODERATION_EVENTS',
);
export const clearModerationEvents = createAction('CLEAR_MODERATION_EVENTS');
export const updateModerationEventsPage = createAction(
    'UPDATE_MODERATION_EVENTS_PAGE',
);
export const updateModerationEventsOrder = createAction(
    'UPDATE_MODERATION_EVENTS_ORDER',
);
export const updateAfterDate = createAction('UPDATE_AFTER_DATE');
export const updateBeforeDate = createAction('UPDATE_BEFORE_DATE');
export const startDownloadModerationEvents = createAction(
    'START_DOWNLOAD_MODERATION_EVENTS',
);
export const failDownloadModerationEvents = createAction(
    'FAIL_DOWNLOAD_MODERATION_EVENTS',
);
export const completeDownloadModerationEvents = createAction(
    'COMPLETE_DOWNLOAD_MODERATION_EVENTS',
);

export function fetchModerationEvents() {
    return (dispatch, getState) => {
        dispatch(startFetchModerationEvents());

        const {
            dashboardModerationQueue: {
                moderationEvents: {
                    page,
                    pageSize,
                    sort: { sortBy, orderBy },
                    afterDate,
                    beforeDate,
                },
            },
            filters,
        } = getState();

        const qs = createQueryStringFromModerationQueueFilters(
            filters,
            afterDate,
            beforeDate,
        );

        return apiRequest
            .get(
                makeGetModerationEventsWithQueryString(
                    qs,
                    page,
                    pageSize,
                    sortBy,
                    orderBy,
                ),
            )
            .then(({ data }) => {
                dispatch(completeFetchModerationEvents(data));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation events',
                        failFetchModerationEvents,
                    ),
                ),
            );
    };
}

export function downloadModerationEvents(data) {
    return dispatch => {
        dispatch(startDownloadModerationEvents());

        try {
            downloadModerationEventsXLSX(data);
            dispatch(completeDownloadModerationEvents());
        } catch (err) {
            dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented downloading moderation events',
                    failDownloadModerationEvents,
                ),
            );
        }
    };
}
