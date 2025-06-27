import { createAction } from 'redux-act';

import {
    logErrorAndDispatchFailure,
    makeGetDownloadLocationsCheckoutSessionURL,
} from '../util/util';

export const startFetchDownloadLimitPaymentUrl = createAction(
    'START_FETCH_DOWNLOAD_LIMIT_PAYMENT_URL',
);
export const failFetchDownloadLimitPaymentUrl = createAction(
    'FAIL_FETCH_DOWNLOAD_LIMIT_PAYMENT_URL',
);
export const hideDownloadLimitPaymentUrlError = createAction(
    'HIDE_DOWNLOAD_LIMIT_PAYMENT_URL_ERROR',
);
export const completeFetchDownloadLimitPaymentUrl = createAction(
    'COMPLETE_FETCH_DOWNLOAD_LIMIT_PAYMENT_URL',
);

export function downloadLimitPaymentUrl() {
    return dispatch => {
        dispatch(startFetchDownloadLimitPaymentUrl());

        return apiRequest
            .post(makeGetDownloadLocationsCheckoutSessionURL())
            .then(({ data }) => {
                dispatch(completeFetchDownloadLimitPaymentUrl(data.url));
            })
            .catch(err => {
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching facilities',
                        failFetchDownloadLimitPaymentUrl,
                    ),
                );
            });
    };
}
