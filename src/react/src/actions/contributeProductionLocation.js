import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    makeGetProductionLocationURL,
    parseContribData,
    makeGetProductionLocationsForPotentialMatches,
} from '../util/util';

export const startFetchSingleProductionLocation = createAction(
    'START_FETCH_SINGLE_PRODUCTION_LOCATION',
);
export const failFetchSingleProductionLocation = createAction(
    'FAIL_FETCH_SINGLE_PRODUCTION_LOCATION',
);
export const completeFetchSingleProductionLocation = createAction(
    'COMPLETE_FETCH_SINGLE_PRODUCTION_LOCATION',
);
export const resetSingleProductionLocation = createAction(
    'RESET_SINGLE_PRODUCTION_LOCATION',
);
export const startFetchProductionLocations = createAction(
    'START_FETCH_PRODUCTION_LOCATIONS',
);
export const failFetchProductionLocations = createAction(
    'FAIL_FETCH_PRODUCTION_LOCATIONS',
);
export const completeFetchProductionLocations = createAction(
    'COMPLETE_FETCH_PRODUCTION_LOCATIONS',
);
export const resetProductionLocations = createAction(
    'RESET_PRODUCTION_LOCATIONS',
);

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

export function createProductionLocation(contribData) {
    const parsedContribData = parseContribData(contribData);

    return async dispatch => {
        dispatch(startCreateProductionLocation());

        try {
            const { data } = await apiRequest.post(
                makeGetProductionLocationURL(),
                parsedContribData,
            );
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

export function updateProductionLocation(contribData, osID) {
    const parsedContribData = parseContribData(contribData);

    return async dispatch => {
        dispatch(startUpdateProductionLocation());

        try {
            const { data } = await apiRequest.patch(
                makeGetProductionLocationURL(osID),
                parsedContribData,
            );
            return dispatch(completeUpdateProductionLocation(data));
        } catch (err) {
            return dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented updating production location',
                    failUpdateProductionLocation,
                ),
            );
        }
    };
}

export function fetchProductionLocations(data) {
    return dispatch => {
        dispatch(startFetchProductionLocations());

        const { name, address, country, size } = data;

        return apiRequest
            .get(
                makeGetProductionLocationsForPotentialMatches(
                    name,
                    address,
                    country,
                    size,
                ),
            )
            .then(response => {
                dispatch(completeFetchProductionLocations(response.data));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching production locations',
                        failFetchProductionLocations,
                    ),
                ),
            );
    };
}

export function fetchProductionLocationByOsId(osID) {
    return dispatch => {
        dispatch(startFetchSingleProductionLocation());

        return apiRequest
            .get(makeGetProductionLocationURL(osID))
            .then(response =>
                dispatch(completeFetchSingleProductionLocation(response.data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching data about that production location',
                        failFetchSingleProductionLocation,
                    ),
                ),
            );
    };
}
