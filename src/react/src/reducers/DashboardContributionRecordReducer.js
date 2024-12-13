/* eslint no-unused-vars: 0 */
import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchingSingleModerationEvent,
    failFetchingSingleModerationEvent,
    completeFetchingSingleModerationEvent,
    startFetchingPotentialMatches,
    failFetchingPotentialMatches,
    completeFetchingPotentialMatches,
    cleanupContributionRecord,
} from '../actions/dashboardContributionRecord';

const initialState = Object.freeze({
    singleModerationEvent: Object.freeze({
        fetching: false,
        error: null,
        data: Object.freeze({}),
    }),
    potentialMatches: Object.freeze({
        matches: Object.freeze([]),
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchingSingleModerationEvent]: state =>
            update(state, {
                singleModerationEvent: {
                    fetching: { $set: true },
                    error: { $set: initialState.singleModerationEvent.error },
                },
            }),
        [failFetchingSingleModerationEvent]: (state, error) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: error },
                },
            }),
        [completeFetchingSingleModerationEvent]: (state, payload) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: initialState.singleModerationEvent.error },
                    data: { $set: payload },
                },
            }),
        [startFetchingPotentialMatches]: state =>
            update(state, {
                potentialMatches: {
                    fetching: { $set: true },
                    error: { $set: initialState.potentialMatches.error },
                },
            }),
        [failFetchingPotentialMatches]: (state, error) =>
            update(state, {
                potentialMatches: {
                    fetching: { $set: initialState.potentialMatches.fetching },
                    error: { $set: error },
                },
            }),
        [completeFetchingPotentialMatches]: (state, payload) =>
            update(state, {
                potentialMatches: {
                    fetching: { $set: initialState.potentialMatches.fetching },
                    error: { $set: initialState.potentialMatches.error },
                    matches: {
                        $set: Array.isArray(payload?.data) ? payload.data : [],
                    },
                },
            }),
        [cleanupContributionRecord]: () => initialState,
    },
    initialState,
);
