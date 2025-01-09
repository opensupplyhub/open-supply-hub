import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchModerationEvents,
    failFetchModerationEvents,
    completeFetchModerationEvents,
    clearModerationEvents,
    updateModerationEventsPage,
    updateModerationEventsOrder,
    updateAfterDate,
    updateBeforeDate,
    startDownloadModerationEvents,
    failDownloadModerationEvents,
    completeDownloadModerationEvents,
} from '../actions/dashboardModerationQueue';

const initialState = Object.freeze({
    moderationEvents: Object.freeze({
        fetching: false,
        error: null,
        moderationEventsList: [],
        count: 0,
        page: 0,
        maxPage: 0,
        pageSize: 25,
        sort: {
            sortBy: 'created_at',
            orderBy: 'desc',
        },
        afterDate: '',
        beforeDate: '',
    }),
    moderationEventsDownloadStatus: Object.freeze({
        downloading: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchModerationEvents]: state =>
            update(state, {
                moderationEvents: {
                    fetching: { $set: true },
                    error: { $set: initialState.moderationEvents.error },
                },
            }),
        [failFetchModerationEvents]: (state, error) =>
            update(state, {
                moderationEvents: {
                    fetching: { $set: initialState.moderationEvents.fetching },
                    error: { $set: error },
                },
            }),
        [completeFetchModerationEvents]: (state, data) =>
            update(state, {
                moderationEvents: {
                    fetching: { $set: initialState.moderationEvents.fetching },
                    error: { $set: initialState.moderationEvents.error },
                    moderationEventsList: {
                        $set: [
                            ...state.moderationEvents.moderationEventsList,
                            ...data.data,
                        ],
                    },
                    count: { $set: data.count },
                },
            }),
        [clearModerationEvents]: state =>
            update(state, {
                moderationEvents: {
                    moderationEventsList: { $set: [] },
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
        [startDownloadModerationEvents]: state =>
            update(state, {
                moderationEventsDownloadStatus: {
                    downloading: { $set: true },
                    error: {
                        $set: initialState.moderationEventsDownloadStatus.error,
                    },
                },
            }),
        [failDownloadModerationEvents]: (state, error) =>
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
        [completeDownloadModerationEvents]: state =>
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
