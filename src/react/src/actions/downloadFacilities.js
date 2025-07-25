import noop from 'lodash/noop';
import { createAction } from 'redux-act';
import includes from 'lodash/includes';

import { logDownload, startLogDownload, failLogDownload } from './logDownload';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    makeGetFacilitiesDownloadURLWithQueryString,
    createQueryStringFromSearchFilters,
    convertFeatureFlagsObjectToListOfActiveFlags,
} from '../util/util';
import { completeSubmitLoginForm } from '../actions/auth';

import {
    FACILITIES_DOWNLOAD_REQUEST_PAGE_SIZE,
    FREE_FACILITIES_DOWNLOAD_LIMIT,
    FACILITIES_DOWNLOAD_LIMIT,
    PRIVATE_INSTANCE,
} from '../util/constants';

export const startFetchDownloadFacilities = createAction(
    'START_FETCH_DOWNLOAD_FACILITIES',
);
export const failFetchDownloadFacilities = createAction(
    'FAIL_FETCH_DOWNLOAD_FACILITIES',
);
export const completeFetchDownloadFacilities = createAction(
    'COMPLETE_FETCH_DOWNLOAD_FACILITIES',
);

export const startFetchNextPageOfDownloadFacilities = createAction(
    'START_FETCH_NEXT_PAGE_OF_DOWNLOAD_FACILITIES',
);
export const failFetchNextPageOfDownloadFacilities = createAction(
    'FAIL_FETCH_NEXT_PAGE_OF_DOWNLOAD_FACILITIES',
);
export const completeFetchNextPageOfDownloadFacilities = createAction(
    'COMPLETE_FETCH_NEXT_PAGE_OF_DOWNLOAD_FACILITIES',
);

export function fetchNextPageOfDownloadFacilities() {
    return (dispatch, getState) => {
        const {
            facilitiesDownload: {
                facilities: { nextPageURL },
            },
        } = getState();

        if (!nextPageURL) {
            return noop();
        }

        dispatch(startFetchNextPageOfDownloadFacilities());

        return apiRequest
            .get(nextPageURL)
            .then(({ data }) =>
                dispatch(completeFetchNextPageOfDownloadFacilities(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching the next page of facilities',
                        failFetchNextPageOfDownloadFacilities,
                    ),
                ),
            );
    };
}

export default function downloadFacilities(format, { isEmbedded }) {
    return (dispatch, getState) => {
        const detail = true;
        const pageSize = FACILITIES_DOWNLOAD_REQUEST_PAGE_SIZE;

        dispatch(startLogDownload());

        dispatch(startFetchDownloadFacilities());

        const {
            filters,
            embeddedMap: { embed },
            auth: {
                user: { user },
            },
            featureFlags: {
                flags: { flags },
            },
        } = getState();

        const activeFlags = convertFeatureFlagsObjectToListOfActiveFlags(flags);
        const isPrivateInstance = includes(activeFlags, PRIVATE_INSTANCE);

        const qs = createQueryStringFromSearchFilters(filters, embed, detail);
        const calcRecordsNumberLeft = (total, downloaded) => total - downloaded;
        const getRecordsLimit = () => {
            if (isPrivateInstance) {
                return FACILITIES_DOWNLOAD_LIMIT;
            }

            return user.allowed_records_number === 0
                ? FREE_FACILITIES_DOWNLOAD_LIMIT
                : user.allowed_records_number;
        };

        return apiRequest
            .get(makeGetFacilitiesDownloadURLWithQueryString(qs, pageSize))
            .then(({ data }) => {
                const recordsLimit = getRecordsLimit();
                const recordsNumber = calcRecordsNumberLeft(
                    recordsLimit,
                    data.count,
                );

                dispatch(completeFetchDownloadFacilities(data));
                dispatch(logDownload(format, { isEmbedded }));
                dispatch(
                    completeSubmitLoginForm({
                        allowed_records_number: recordsNumber,
                    }),
                );
            })
            .catch(err => {
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching facilities',
                        failFetchDownloadFacilities,
                    ),
                );
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented the facilities download',
                        failLogDownload,
                    ),
                );
            });
    };
}
