import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    makeGetProductionLocationByOsIdURL,
    makeGetProductionLocationsForSearchMatches,
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

export function fetchProductionLocationByOsId(osID) {
    return dispatch => {
        dispatch(startFetchSingleProductionLocation());

        return apiRequest
            .get(makeGetProductionLocationByOsIdURL(osID))
            .then(({ data }) =>
                dispatch(completeFetchSingleProductionLocation(data)),
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

export function fetchProductionLocations(data) {
    return async dispatch => {
        dispatch(startFetchProductionLocations());

        const { name, address, country, fromIndex } = data;

        return apiRequest
            .get(
                makeGetProductionLocationsForSearchMatches(
                    name,
                    address,
                    country,
                    fromIndex,
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
