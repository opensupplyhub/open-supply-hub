import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import { logErrorAndDispatchFailure } from '../util/util';

export const startFetchPartnerGroupContributors = createAction(
    'START_FETCH_PARTNER_GROUP_CONTRIBUTORS',
);
export const failFetchPartnerGroupContributors = createAction(
    'FAIL_FETCH_PARTNER_GROUP_CONTRIBUTORS',
);
export const completeFetchPartnerGroupContributors = createAction(
    'COMPLETE_FETCH_PARTNER_GROUP_CONTRIBUTORS',
);

const fetchURL = '/api/partner-group-contributors/?limit=100';

export const fetchPartnerGroupContributors = () => dispatch => {
    dispatch(startFetchPartnerGroupContributors());

    return apiRequest
        .get(fetchURL)
        .then(({ data }) =>
            dispatch(completeFetchPartnerGroupContributors(data)),
        )
        .catch(err =>
            dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented fetching partner group contributors',
                    failFetchPartnerGroupContributors,
                ),
            ),
        );
};

export const fetchPartnerGroupContributorsIfNeeded = () => (
    dispatch,
    getState,
) => {
    const { data, fetching } = getState().partnerGroupContributors;
    if (data !== null || fetching) return;
    dispatch(fetchPartnerGroupContributors());
};
