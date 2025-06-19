import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchDownloadLimitPaymentUrl,
    failFetchDownloadLimitPaymentUrl,
    hideDownloadLimitPaymentUrlError,
    completeFetchDownloadLimitPaymentUrl,
} from '../actions/downloadLimit';

const initialState = Object.freeze({
    payment: Object.freeze({
        fetching: false,
        error: null,
        url: null,
    }),
});

export default createReducer(
    {
        [startFetchDownloadLimitPaymentUrl]: state =>
            update(state, {
                payment: {
                    fetching: { $set: true },
                    error: { $set: null },
                    url: { $set: null },
                },
            }),
        [failFetchDownloadLimitPaymentUrl]: (state, payload) =>
            update(state, {
                payment: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [hideDownloadLimitPaymentUrlError]: state =>
            update(state, {
                payment: {
                    error: { $set: initialState.error },
                },
            }),
        [completeFetchDownloadLimitPaymentUrl]: (state, payload) =>
            update(state, {
                payment: {
                    fetching: { $set: false },
                    error: { $set: null },
                    url: {
                        $set: payload,
                    },
                },
            }),
    },
    initialState,
);
