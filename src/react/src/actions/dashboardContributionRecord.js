import { createAction } from 'redux-act';
import apiRequest from '../util/apiRequest';
import {
    makeGetModerationEvent,
    logErrorAndDispatchFailure,
} from '../util/util';

export const startFetchingSingleModerationEvent = createAction(
    'START_FETCHING_SINGLE_MODERATION_EVENT',
);
export const failFetchingSingleModerationEvent = createAction(
    'FAIL_FETCHING_SINGLE_MODERATION_EVENT',
);
export const completeFetchingSingleModerationEvent = createAction(
    'COMPLETE_FETCHING_SINGLE_MODERATION_EVENT',
);
export const startFetchingPotentialMatches = createAction(
    'START_FETCHING_POTENTIAL_MATCHES',
);
export const failFetchingPotentialMatches = createAction(
    'FAIL_FETCHING_POTENTIAL_MATCHES',
);
export const completeFetchingPotentialMatches = createAction(
    'COMPLETE_FETCHING_POTENTIAL_MATCHES',
);
export const cleanupContributionRecord = createAction(
    'CLEANUP_CONTRIBUTION_RECORD',
);

// TODO: Remove mock data and replace with actual API call as part  of /v1/production-locations endpoint
const potentialMatchesMockData = [
    {
        os_id: 'CY2021280D1DTN7',
        name: 'M.K.SUNDHERAM LTD',
        address: '1523 Main St, Manhattan, NY - USA',
        sector: ['Footwear'],
        parent_company: 'Intimate Apparels Ltd',
        product_type: ['Accessories'],
        location_type: [],
        processing_type: ['Design', 'Knitting'],
        number_of_workers: {
            min: 500,
            max: 5000,
        },
        coordinates: {
            lat: 91.7896718,
            lng: 22.2722865,
        },
        local_name: 'CHINA,FUZHOU STARRISING',
        description:
            'HUGO BOSS list of active finished goods suppliers March 2019',
        business_url: '',
        minimum_order_quantity: '',
        average_lead_time: '',
        percent_female_workers: 23,
        affiliations: [],
        certifications_standards_regulations: [],
        historical_os_id: [],
        country: {
            name: 'Germany',
            alpha_2: 'DE',
            alpha_3: 'DEU',
            numeric: '276',
        },
        claim_status: 'unclaimed',
    },
];

export function fetchSingleModerationEvent(moderationID) {
    return async dispatch => {
        dispatch(startFetchingSingleModerationEvent());

        return apiRequest
            .get(makeGetModerationEvent(moderationID))
            .then(({ data }) => {
                dispatch(completeFetchingSingleModerationEvent(data));
            })
            .catch(err => {
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation event',
                        failFetchingSingleModerationEvent,
                    ),
                );
            });
    };
}

// TODO: Apply OpenSearch results here
export function fetchPotentialMatches() {
    return async dispatch => {
        dispatch(startFetchingPotentialMatches());

        // TODO: Replace the mock implementation with an actual API call as part of /v1/production-locations endpoint
        return new Promise(resolve => {
            setTimeout(() => resolve({ data: potentialMatchesMockData }), 1000);
        })
            .then(({ data }) =>
                dispatch(completeFetchingPotentialMatches(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching potential matches',
                        failFetchingPotentialMatches,
                    ),
                ),
            );
    };
}
