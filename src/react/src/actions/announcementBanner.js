import debounce from 'lodash/debounce';
import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import {
    makeGetAnnouncementBannerURL,
    logErrorAndDispatchFailure,
} from '../util/util';

export const failFetchAnnouncementBanner = createAction(
    'FAIL_FETCH_ANNOUNCEMENT_BANNER',
);
export const completeFetchAnnouncementBanner = createAction(
    'COMPLETE_FETCH_ANNOUNCEMENT_BANNER',
);

// Requests are fired again on every navigation, so a slow earlier response
// can land after a newer one. Only the most recent request may update state.
let latestRequestId = 0;

const requestBanner = dispatch => {
    latestRequestId += 1;
    const requestId = latestRequestId;

    return apiRequest
        .get(makeGetAnnouncementBannerURL())
        .then(({ data }) => {
            if (requestId !== latestRequestId) {
                return null;
            }

            return dispatch(completeFetchAnnouncementBanner(data));
        })
        .catch(err =>
            dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented fetching the announcement banner',
                    failFetchAnnouncementBanner,
                ),
            ),
        );
};

export function fetchAnnouncementBanner() {
    return dispatch => requestBanner(dispatch);
}

const debouncedRefresh = debounce(requestBanner, 300);

export function refreshAnnouncementBanner() {
    return dispatch => debouncedRefresh(dispatch);
}
