/* eslint no-unused-vars: 0 */
import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    // TODO: Remove makeGetProductionLocationByOsIdURL
    makeGetProductionLocationByOsIdURL,
    makeGetProductionLocationURL,
} from '../util/util';

// This action is needed to fetch existing production location by OS ID
// It is using in src/react/src/components/Contribute/SearchByOsIdResult.jsx
// but response data is not rendered because 5 and 5b screens in progress.
export const startFetchingSingleProductionLocation = createAction(
    'START_FETCHING_SINGLE_PRODUCTION_LOCATION',
);
export const failFetchingSingleProductionLocation = createAction(
    'FAIL_FETCHING_SINGLE_PRODUCTION_LOCATION',
);
export const completeFetchingSingleProductionLocation = createAction(
    'COMPLETE_FETCHING_SINGLE_PRODUCTION_LOCATION',
);
export const resetSingleProductionLocation = createAction(
    'RESET_SINGLE_PRODUCTION_LOCATION',
);

// TODO: Use modified makeGetProductionLocationByOsIdURL
export const startCreateProductionLocation = createAction(
    'START_CREATE_PRODUCTION_LOCATION',
);

export const completeCreateProductionLocation = createAction(
    'COMPLETE_CREATE_PRODUCTION_LOCATION',
);

export const failCreateProductionLocation = createAction(
    'FAIL_CREATE_PRODUCTION_LOCATION',
);

export const startUpdateProductionLocation = createAction(
    'START_UPDATE_PRODUCTION_LOCATION',
);

export const completeUpdateProductionLocation = createAction(
    'COMPLETE_UPDATE_PRODUCTION_LOCATION',
);

export const failUpdateProductionLocation = createAction(
    'FAIL_UPDATE_PRODUCTION_LOCATION',
);

export function fetchProductionLocationByOsId(osID) {
    return async dispatch => {
        dispatch(startFetchingSingleProductionLocation());

        try {
            const { data } = await apiRequest.get(
                makeGetProductionLocationByOsIdURL(osID),
            );
            return dispatch(completeFetchingSingleProductionLocation(data));
        } catch (err) {
            return dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented fetching data about that production location',
                    failFetchingSingleProductionLocation,
                ),
            );
        }
    };
}

export function createProductionLocation(data) {
    const {
        name,
        address,
        country,
        sector,
        productType,
        locationType,
        processingType,
        numberOfWorkers,
        parentCompany,
    } = data;

    /*
    {
        "source": "API",
        "name": "string",
        "address": "string",
        "country": "string",
        "sector": [
            "string"
        ],
        "parent_company": "string",
        "product_type": [
            "string"
        ],
        "location_type": [
            "string"
        ],
        "processing_type": [
            "string"
        ],
        "number_of_workers": {
            "min": 0,
            "max": 0
        },
        "coordinates": {
            "lat": 0,
            "lng": 0
        }
    }
    */

    const mockedData = {
        source: 'SLC', // Setup this automatically
        name: 'Production Location Name',
        address: 'David, Chiriquí Province, Panama',
        country: 'PA',
        sector: ['Apparel', 'Food'],
        parent_company: 'Some parent company',
        product_type: ['Salt'],
        location_type: ['Assembly'],
        processing_type: ['Chemical Synthesis'],
        number_of_workers: {
            min: 10,
            max: 20,
        },
        // TODO: what about coordinates?
    };

    return async dispatch => {
        dispatch(startCreateProductionLocation());

        try {
            const { response } = await apiRequest.post(
                makeGetProductionLocationURL(),
                mockedData,
            );
            /*
            {
                created_at: "2024-12-27T12:51:52.729339Z"
                moderation_id: "c98cb4c4-6c91-4a7b-8844-858802049e0a"
                moderation_status: "PENDING"
            }
            */
            console.log('@@@ response is: ', response);
            return dispatch(completeCreateProductionLocation(response));
        } catch (err) {
            return dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented creating production location',
                    failCreateProductionLocation,
                ),
            );
        }
    };
}

export function updateProductionLocation(osID) {
    return async dispatch => {
        dispatch(startUpdateProductionLocation());

        try {
            const { data } = await apiRequest.update(
                makeGetProductionLocationURL(osID),
            );
            return dispatch(completeUpdateProductionLocation(data));
        } catch (err) {
            return dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented creating production location',
                    failUpdateProductionLocation,
                ),
            );
        }
    };
}
