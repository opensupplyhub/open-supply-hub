import { createAction } from 'redux-act';
import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    makeGetDownloadLocationsCheckoutSessionURL,
} from '../util/util';

export const startFetchDownloadLimitCheckoutUrl = createAction(
    'START_FETCH_DOWNLOAD_LIMIT_CHECKOUT_URL',
);
export const failFetchDownloadLimitCheckoutUrl = createAction(
    'FAIL_FETCH_DOWNLOAD_LIMIT_CHECKOUT_URL',
);
export const hideDownloadLimitCheckoutUrlError = createAction(
    'HIDE_DOWNLOAD_LIMIT_CHECKOUT_URL_ERROR',
);
export const completeFetchDownloadLimitCheckoutUrl = createAction(
    'COMPLETE_FETCH_DOWNLOAD_LIMIT_CHECKOUT_URL',
);

export function downloadLimitCheckoutUrl() {
    return dispatch => {
        dispatch(startFetchDownloadLimitCheckoutUrl());

        return apiRequest
            .post(makeGetDownloadLocationsCheckoutSessionURL(), {})
            .then(({ data }) => {
                dispatch(completeFetchDownloadLimitCheckoutUrl(data.url));
            })
            .catch(err => {
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching checkout url',
                        failFetchDownloadLimitCheckoutUrl,
                    ),
                );
            });
    };
}
