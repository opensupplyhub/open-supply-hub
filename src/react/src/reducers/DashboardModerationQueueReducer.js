import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchingModerationEvents,
    failFetchingModerationEvents,
    completeFetchingModerationEvents,
    startDownloadingModerationEvents,
    failDownloadingModerationEvents,
    completeDownloadingModerationEvents,
} from '../actions/dashboardModerationQueue';

const initialState = Object.freeze({
    moderationEvents: Object.freeze({
        fetching: false,
        error: null,
        events: [],
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
                    events: { $set: data.data },
                    count: { $set: data.count },
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
