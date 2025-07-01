import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchDownloadLimitCheckoutUrl,
    failFetchDownloadLimitCheckoutUrl,
    hideDownloadLimitCheckoutUrlError,
    completeFetchDownloadLimitCheckoutUrl,
} from '../actions/downloadLimit';

const initialState = Object.freeze({
    checkout: Object.freeze({
        fetching: false,
        error: null,
        checkoutUrl: null,
    }),
});

export default createReducer(
    {
        [startFetchDownloadLimitCheckoutUrl]: state =>
            update(state, {
                checkout: {
                    fetching: { $set: true },
                    error: { $set: null },
                    checkoutUrl: { $set: null },
                },
            }),
        [failFetchDownloadLimitCheckoutUrl]: (state, payload) =>
            update(state, {
                checkout: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [hideDownloadLimitCheckoutUrlError]: state =>
            update(state, {
                checkout: {
                    error: { $set: initialState.error },
                },
            }),
        [completeFetchDownloadLimitCheckoutUrl]: (state, payload) =>
            update(state, {
                checkout: {
                    fetching: { $set: false },
                    error: { $set: null },
                    checkoutUrl: {
                        $set: payload,
                    },
                },
            }),
    },
    initialState,
);
