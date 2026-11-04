import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import {
    makeGetAnnouncementBannerURL,
    logErrorAndDispatchFailure,
} from '../util/util';

export const startFetchAnnouncementBanner = createAction(
    'START_FETCH_ANNOUNCEMENT_BANNER',
);
export const failFetchAnnouncementBanner = createAction(
    'FAIL_FETCH_ANNOUNCEMENT_BANNER',
);
export const completeFetchAnnouncementBanner = createAction(
    'COMPLETE_FETCH_ANNOUNCEMENT_BANNER',
);

export function fetchAnnouncementBanner() {
    return dispatch => {
        dispatch(startFetchAnnouncementBanner());

        return apiRequest
            .get(makeGetAnnouncementBannerURL())
            .then(({ data }) => dispatch(completeFetchAnnouncementBanner(data)))
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
}
