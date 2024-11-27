import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchingModerationEvents,
    failFetchingModerationEvents,
    completeFetchingModerationEvents,
    clearModerationEvents,
    updateModerationEventsPage,
    updateModerationEventsOrder,
    updateAfterDate,
    updateBeforeDate,
    startDownloadingModerationEvents,
    failDownloadingModerationEvents,
    completeDownloadingModerationEvents,
} from '../actions/dashboardModerationQueue';

const initialState = Object.freeze({
    moderationEvents: Object.freeze({
        fetching: false,
        error: null,
        events: [],
        count: 0,
        page: 0,
        maxPage: 0,
        pageSize: 5,
        sort: {
            sortBy: 'created_at',
            orderBy: 'desc',
        },
        afterDate: null,
        beforeDate: null,
    }),
    moderationEventsDownloadStatus: Object.freeze({
        downloading: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchingModerationEvents]: state =>
            update(state, {
                moderationEvents: {
                    fetching: { $set: true },
                    error: { $set: initialState.moderationEvents.error },
                },
            }),
        [failFetchingModerationEvents]: (state, error) =>
            update(state, {
                moderationEvents: {
                    fetching: { $set: initialState.moderationEvents.fetching },
                    error: { $set: error },
                },
            }),
        [completeFetchingModerationEvents]: (state, data) =>
            update(state, {
                moderationEvents: {
                    fetching: { $set: initialState.moderationEvents.fetching },
                    error: { $set: initialState.moderationEvents.error },
                    events: {
                        $set: [...state.moderationEvents.events, ...data.data],
                    },
                    count: { $set: data.count },
                },
            }),
        [clearModerationEvents]: state =>
            update(state, {
                moderationEvents: {
                    events: { $set: [] },
                },
            }),
        [updateModerationEventsPage]: (state, { page, maxPage, pageSize }) =>
            update(state, {
                moderationEvents: {
                    page: { $set: page },
                    maxPage: { $set: maxPage },
                    pageSize: { $set: pageSize },
                },
            }),
        [updateModerationEventsOrder]: (state, { sortBy, orderBy }) =>
            update(state, {
                moderationEvents: {
                    sort: {
                        sortBy: { $set: sortBy },
                        orderBy: { $set: orderBy },
                    },
                },
            }),
        [updateAfterDate]: (state, afterDate) =>
            update(state, {
                moderationEvents: {
                    afterDate: { $set: afterDate },
                },
            }),
        [updateBeforeDate]: (state, beforeDate) =>
            update(state, {
                moderationEvents: {
                    beforeDate: { $set: beforeDate },
                },
            }),
        [startDownloadingModerationEvents]: state =>
            update(state, {
                moderationEventsDownloadStatus: {
                    downloading: { $set: true },
                    error: {
                        $set: initialState.moderationEventsDownloadStatus.error,
                    },
                },
            }),
        [failDownloadingModerationEvents]: (state, error) =>
            update(state, {
                moderationEventsDownloadStatus: {
                    downloading: {
                        $set:
                            initialState.moderationEventsDownloadStatus
                                .downloading,
                    },
                    error: { $set: error },
                },
            }),
        [completeDownloadingModerationEvents]: state =>
            update(state, {
                moderationEventsDownloadStatus: {
                    downloading: {
                        $set:
                            initialState.moderationEventsDownloadStatus
                                .downloading,
                    },
                    error: {
                        $set: initialState.moderationEventsDownloadStatus.error,
                    },
                },
            }),
    },
    initialState,
);
