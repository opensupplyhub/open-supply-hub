import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    makeGetProductionLocationByOsIdURL,
} from '../util/util';

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

export function fetchProductionLocationByOsId(osID) {
    return dispatch => {
        dispatch(startFetchingSingleProductionLocation());

        return apiRequest
            .get(makeGetProductionLocationByOsIdURL(osID))
            .then(({ data }) =>
                dispatch(completeFetchingSingleProductionLocation(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching data about that production location',
                        failFetchingSingleProductionLocation,
                    ),
                ),
            );
    };
}
