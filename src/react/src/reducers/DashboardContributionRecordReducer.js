import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchSingleModerationEvent,
    failFetchSingleModerationEvent,
    completeFetchSingleModerationEvent,
    startFetchPotentialMatches,
    failFetchPotentialMatches,
    completeFetchPotentialMatches,
    startUpdateSingleModerationEvent,
    failUpdateSingleModerationEvent,
    completeUpdateSingleModerationEvent,
    startCreateProductionLocationFromModerationEvent,
    failCreateProductionLocationFromModerationEvent,
    completeCreateProductionLocationFromModerationEvent,
    startConfirmPotentialMatchFromModerationEvent,
    failConfirmPotentialMatchFromModerationEvent,
    completeConfirmPotentialMatchFromModerationEvent,
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
        [startFetchSingleModerationEvent]: state =>
            update(state, {
                singleModerationEvent: {
                    fetching: { $set: true },
                    error: { $set: initialState.singleModerationEvent.error },
                },
            }),
        [failFetchSingleModerationEvent]: (state, error) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: error },
                },
            }),
        [completeFetchSingleModerationEvent]: (state, payload) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: initialState.singleModerationEvent.error },
                    data: { $set: payload },
                },
            }),
        [startFetchPotentialMatches]: state =>
            update(state, {
                potentialMatches: {
                    fetching: { $set: true },
                    error: { $set: initialState.potentialMatches.error },
                },
            }),
        [failFetchPotentialMatches]: (state, error) =>
            update(state, {
                potentialMatches: {
                    fetching: { $set: initialState.potentialMatches.fetching },
                    error: { $set: Array.isArray(error) ? error[0] : error },
                },
            }),
        [completeFetchPotentialMatches]: (state, payload) =>
            update(state, {
                potentialMatches: {
                    fetching: { $set: initialState.potentialMatches.fetching },
                    error: { $set: initialState.potentialMatches.error },
                    matches: {
                        $set: Array.isArray(payload?.data) ? payload.data : [],
                    },
                },
            }),
        [startUpdateSingleModerationEvent]: state =>
            update(state, {
                singleModerationEvent: {
                    fetching: { $set: true },
                    error: { $set: initialState.singleModerationEvent.error },
                },
            }),
        [failUpdateSingleModerationEvent]: (state, error) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: error },
                },
            }),
        [completeUpdateSingleModerationEvent]: (state, payload) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: initialState.singleModerationEvent.error },
                    data: { $set: payload },
                },
            }),
        [startCreateProductionLocationFromModerationEvent]: state =>
            update(state, {
                singleModerationEvent: {
                    fetching: { $set: true },
                    error: { $set: initialState.singleModerationEvent.error },
                },
            }),
        [failCreateProductionLocationFromModerationEvent]: (state, error) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: error },
                },
            }),
        [completeCreateProductionLocationFromModerationEvent]: (
            state,
            payload,
        ) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: initialState.singleModerationEvent.error },
                    data: {
                        $merge: payload,
                    },
                },
            }),
        [startConfirmPotentialMatchFromModerationEvent]: state =>
            update(state, {
                singleModerationEvent: {
                    fetching: { $set: true },
                    error: { $set: initialState.singleModerationEvent.error },
                },
            }),
        [failConfirmPotentialMatchFromModerationEvent]: (state, error) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: error },
                },
            }),
        [completeConfirmPotentialMatchFromModerationEvent]: (state, payload) =>
            update(state, {
                singleModerationEvent: {
                    fetching: {
                        $set: initialState.singleModerationEvent.fetching,
                    },
                    error: { $set: initialState.singleModerationEvent.error },
                    data: {
                        $merge: payload,
                    },
                },
            }),
        [cleanupContributionRecord]: () => initialState,
    },
    initialState,
);
