import { createAction } from 'redux-act';

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

        // dispatch(failFetchDownloadLimitPaymentUrl('Something goes wrong'));

        dispatch(
            completeFetchDownloadLimitPaymentUrl(
                'http://localhost:6543/facilities/?success=true',
            ),
        );
    };
}
