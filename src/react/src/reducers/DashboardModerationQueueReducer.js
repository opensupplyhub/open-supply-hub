import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchingModerationEvents,
    failFetchingModerationEvents,
    completeFetchingModerationEvents,
} from '../actions/dashboardModerationQueue';

const initialState = Object.freeze({
    moderationEvents: Object.freeze({
        fetching: false,
        error: null,
        events: [],
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
                    events: { $set: data },
                },
            }),
    },
    initialState,
);
