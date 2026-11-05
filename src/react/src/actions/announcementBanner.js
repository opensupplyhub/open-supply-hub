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

export function fetchAnnouncementBanner() {
    return dispatch =>
        apiRequest
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
}
