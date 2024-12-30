/* eslint no-unused-vars: 0 */
import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    // TODO: Remove makeGetProductionLocationByOsIdURL
    makeGetProductionLocationByOsIdURL,
    makeGetProductionLocationURL,
    generateRangeField,
    extractProductionLocationContributionValues,
} from '../util/util';

import { DATA_SOURCES_ENUM } from '../util/constants';

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
// TODO: This actions should use 'src/react/src/reducers/DashboardContributionRecordReducer.js' from OSDEV-1117
// Regular contributor can get moderation event
// OS ID will be rendered depending on request_type and os_id presence. But only moderator can change it's status
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

export function createProductionLocation(contribData) {
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
    } = contribData;

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

    const parsedContribData = {
        source: DATA_SOURCES_ENUM.SLC,
        name,
        address,
        country: country.value,
        sector: extractProductionLocationContributionValues(sector),
        parent_company: extractProductionLocationContributionValues(
            parentCompany,
        ),
        product_type: extractProductionLocationContributionValues(productType),
        location_type: extractProductionLocationContributionValues(
            locationType,
        ),
        processing_type: extractProductionLocationContributionValues(
            processingType,
        ),
        // TODO: refactor later
        number_of_workers: generateRangeField(numberOfWorkers.value),
    };

    return async dispatch => {
        dispatch(startCreateProductionLocation());

        try {
            const { data } = await apiRequest.post(
                makeGetProductionLocationURL(),
                parsedContribData,
            );
            /*
            {
                created_at: "2024-12-27T12:51:52.729339Z"
                moderation_id: "c98cb4c4-6c91-4a7b-8844-858802049e0a"
                moderation_status: "PENDING"
            }
            */
            console.log('@@@ response data is: ', data);
            return dispatch(completeCreateProductionLocation(data));
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
