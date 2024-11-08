import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchingModerationEvent,
    failFetchingModerationEvent,
    completeFetchingModerationEvent,
    startFetchingPotentialMatches,
    failFetchingPotentialMatches,
    completeFetchingPotentialMatches,
    cleanupContributionRecord,
} from '../actions/dashboardContributionRecord';

const initialState = Object.freeze({
    moderationEvent: Object.freeze({
        fetching: false,
        error: null,
        event: Object.freeze({}),
    }),
    potentialMatches: Object.freeze({
        potentialMatches: Object.freeze([]),
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchingModerationEvent]: state =>
            update(state, {
                moderationEvent: {
                    fetching: { $set: true },
                    error: { $set: initialState.moderationEvent.error },
                },
            }),
        [failFetchingModerationEvent]: (state, error) =>
            update(state, {
                moderationEvent: {
                    fetching: { $set: initialState.moderationEvent.fetching },
                    error: { $set: error },
                },
            }),
        [completeFetchingModerationEvent]: (state, payload) =>
            update(state, {
                moderationEvent: {
                    fetching: { $set: initialState.moderationEvent.fetching },
                    error: { $set: initialState.moderationEvent.error },
                    event: { $set: payload },
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
                    potentialMatches: { $set: payload },
                },
            }),
        [cleanupContributionRecord]: () => initialState,
    },
    initialState,
);
