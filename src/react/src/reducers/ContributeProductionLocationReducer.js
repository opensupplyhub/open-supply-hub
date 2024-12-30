/* eslint no-unused-vars: 0 */
import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchingSingleProductionLocation,
    failFetchingSingleProductionLocation,
    completeFetchingSingleProductionLocation,
    resetSingleProductionLocation,
    startCreateProductionLocation,
    completeCreateProductionLocation,
    failCreateProductionLocation,
    startUpdateProductionLocation,
    completeUpdateProductionLocation,
    failUpdateProductionLocation,
} from '../actions/contributeProductionLocation';

const initialState = Object.freeze({
    singleProductionLocation: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchingSingleProductionLocation]: state =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: true },
                    error: { $set: null },
                    data: { $set: null },
                },
            }),
        [failFetchingSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchingSingleProductionLocation]: (state, payload) =>
            update(state, {
                singleProductionLocation: {
                    fetching: { $set: false },
                    error: { $set: null },
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
        [startCreateProductionLocation]: state => update(state, {}),
        [completeCreateProductionLocation]: state => update(state, {}),
        [failCreateProductionLocation]: state => update(state, {}),
        [startUpdateProductionLocation]: state => update(state, {}),
        [completeUpdateProductionLocation]: state => update(state, {}),
        [failUpdateProductionLocation]: state => update(state, {}),
    },
    initialState,
);
