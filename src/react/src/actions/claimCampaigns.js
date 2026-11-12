import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import { logErrorAndDispatchFailure } from '../util/util';

export const startFetchClaimCampaigns = createAction(
    'START_FETCH_CLAIM_CAMPAIGNS',
);
export const failFetchClaimCampaigns = createAction(
    'FAIL_FETCH_CLAIM_CAMPAIGNS',
);
export const completeFetchClaimCampaigns = createAction(
    'COMPLETE_FETCH_CLAIM_CAMPAIGNS',
);

export function fetchClaimCampaigns() {
    return dispatch => {
        dispatch(startFetchClaimCampaigns());

        return apiRequest
            .get('/api/claim-campaigns/')
            .then(({ data }) => dispatch(completeFetchClaimCampaigns(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching claim campaigns',
                        failFetchClaimCampaigns,
                    ),
                ),
            );
    };
}
