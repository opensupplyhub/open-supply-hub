/* eslint no-unused-vars: 0 */
import { createReducer } from 'redux-act';
import update from 'immutability-helper';
import {
    startFetchSingleProductionLocation,
    failFetchSingleProductionLocation,
    completeFetchSingleProductionLocation,
    resetSingleProductionLocation,
    startCreateProductionLocation,
    completeCreateProductionLocation,
    failCreateProductionLocation,
    startUpdateProductionLocation,
    completeUpdateProductionLocation,
    failUpdateProductionLocation,
    startFetchProductionLocations,
    failFetchProductionLocations,
    completeFetchProductionLocations,
    resetProductionLocations,
} from '../actions/contributeProductionLocation';

const initialState = Object.freeze({
    singleProductionLocation: Object.freeze({
        data: {},
        fetching: false,
        error: null,
    }),
    productionLocations: Object.freeze({
        count: 0,
        data: [],
        fetching: false,
        error: null,
    }),
    pendingModerationEvent: Object.freeze({
        data: {},
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        // Single Production Location
        [startFetchSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: true },
                    error: {
                        $set: initialState.singleProductionLocation.error,
                    },
                    data: { $set: initialState.singleProductionLocation.data },
                },
            }),
        [failFetchSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: {
                        $set: initialState.singleProductionLocation.fetching,
                    },
                    error: { $set: payload },
                },
            }),
        [completeFetchSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: {
                        $set: initialState.singleProductionLocation.fetching,
                    },
                    error: {
                        $set: initialState.singleProductionLocation.error,
                    },
                    data: { $set: payload },
                },
            }),
        [resetSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    $set: initialState.singleProductionLocation,
                },
            }),
        /*
            Design Docs: https://opensupplyhub.github.io/open-supply-hub-api-docs/
            Both endpoints create moderation event for particular record

            1. response of POST /api/v1/production-locations
            202
            {
                "moderation_id": "123e4567-e89b-12d3-a456-426614174000",
                "moderation_status": "PENDING",
                "created_at": "2024-12-27T10:37:20.309Z"
            }

            400
            {
                "detail": "The request body is invalid.",
                "errors": [
                    {
                    "field": "non_field_errors",
                    "detail": "Invalid data. Expected a dictionary (object), but got list."
                    }
                ]
            }
            
            2. PATCH api/v1/production-locations/{os_id}/
            202
            {
                "os_id": "ID2024331V7D4T9",
                "moderation_id": "123e4567-e89b-12d3-a456-426614174000",
                "moderation_status": "PENDING",
                "created_at": "2024-12-27T10:39:20.338Z"
            }

            400
            {
                "detail": "The request body is invalid.",
                "errors": [
                    {
                        "field": "non_field_errors",
                        "detail": "Invalid data. Expected a dictionary (object), but got list."
                    }
                ]
            }

        */
        [startCreateProductionLocation]: state =>
            update(state, {
                pendingModerationEvent: {
                    fetching: { $set: true },
                    error: {
                        $set: initialState.pendingModerationEvent.error,
                    },
                    data: { $set: initialState.pendingModerationEvent.data },
                },
            }),
        [completeCreateProductionLocation]: (state, payload) =>
            update(state, {
                pendingModerationEvent: {
                    fetching: {
                        $set: initialState.pendingModerationEvent.fetching,
                    },
                    error: {
                        $set: initialState.pendingModerationEvent.error,
                    },
                    data: { $set: payload },
                },
            }),
        [failCreateProductionLocation]: (state, payload) =>
            update(state, {
                pendingModerationEvent: {
                    fetching: {
                        $set: initialState.pendingModerationEvent.fetching,
                    },
                    error: { $set: payload },
                },
            }),
        [startUpdateProductionLocation]: state => update(state, {}),
        [completeUpdateProductionLocation]: state => update(state, {}),
        [failUpdateProductionLocation]: state => update(state, {}),

        // Production Locations
        [startFetchProductionLocations]: state =>
            update(state, {
                productionLocations: {
                    fetching: { $set: true },
                    error: { $set: initialState.productionLocations.error },
                    count: { $set: initialState.productionLocations.count },
                    data: { $set: initialState.productionLocations.data },
                },
            }),
        [failFetchProductionLocations]: (state, payload) =>
            update(state, {
                productionLocations: {
                    fetching: {
                        $set: initialState.productionLocations.fetching,
                    },
                    error: { $set: payload },
                },
            }),
        [completeFetchProductionLocations]: (state, payload) =>
            update(state, {
                productionLocations: {
                    fetching: {
                        $set: initialState.productionLocations.fetching,
                    },
                    error: { $set: initialState.productionLocations.error },
                    count: { $set: payload.count },
                    data: { $set: payload.data },
                },
            }),
        [resetProductionLocations]: state =>
            update(state, {
                productionLocations: {
                    $set: initialState.productionLocations,
                },
            }),
    },
    initialState,
);
