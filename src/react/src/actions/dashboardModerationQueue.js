import { createAction } from 'redux-act';
import {
    logErrorAndDispatchFailure,
    downloadModerationEventsXLSX,
    makeGetModerationEventsWithQueryString,
    createQueryStringFromModerationQueueFilters,
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
export const updateModerationEventsPage = createAction(
    'UPDATE_MODERATION_EVENTS_PAGE',
);
export const updateModerationEventsOrder = createAction(
    'UPDATE_MODERATION_EVENTS_ORDER',
);
export const updateAfterDate = createAction('UPDATE_AFTER_DATE');
export const updateBeforeDate = createAction('UPDATE_BEFORE_DATE');
export const startDownloadingModerationEvents = createAction(
    'START_DOWNLOADING_MODERATION_EVENTS',
);
export const failDownloadingModerationEvents = createAction(
    'FAIL_DOWNLOADING_MODERATION_EVENTS',
);
export const completeDownloadingModerationEvents = createAction(
    'COMPLETE_DOWNLOADING_MODERATION_EVENTS',
);

export function fetchModerationEvents() {
    return async (dispatch, getState) => {
        dispatch(startFetchingModerationEvents());

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
