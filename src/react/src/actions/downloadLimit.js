import { createAction } from 'redux-act';

export const startFetchDownloadLimitPaymentUrl = createAction(
    'START_FETCH_DOWNLOAD_LIMIT_PAYMENT_URL',
);
export const failFetchDownloadLimitPaymentUrl = createAction(
    'FAIL_FETCH_DOWNLOAD_LIMIT_PAYMENT_URL',
);
export const completeFetchDownloadLimitPaymentUrl = createAction(
    'COMPLETE_FETCH_DOWNLOAD_LIMIT_PAYMENT_URL',
);

export default function downloadLimitPaymentUrl() {
    return dispatch => {
        dispatch(startFetchDownloadLimitPaymentUrl());

        const testUrl = 'http://localhost:6543/facilities/?success=true';

        dispatch(completeFetchDownloadLimitPaymentUrl(testUrl));
    };
}
