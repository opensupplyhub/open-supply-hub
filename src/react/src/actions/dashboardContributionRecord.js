import { createAction } from 'redux-act';
import { logErrorAndDispatchFailure } from '../util/util';

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

// TODO: Remove mock data and replace with actual API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1347
const eventMockData = {
    moderation_id: 28,
    created_at: '2024-06-13T15:30:20.287Z',
    updated_at: '2024-09-20T11:35:20.287Z',
    os_id: 'FN2071250D1DTN7',
    cleaned_data: {
        name: 'Benetton 6784',
        address: 'Bangladesh,Salman Adnan (Pvt) Ltd,35-B/I',
        country: {
            name: 'Haiti',
            alpha_2: 'HT',
            alpha_3: 'HTI',
            numeric: '332',
        },
    },
    contributor_id: 0,
    contributor_name: 'SALIM & BROTHERS LTD',
    request_type: 'CREATE',
    source: 'API',
    moderation_status: 'PENDING',
    moderation_decision_date: null,
    claim_id: 56,
};
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

// eslint-disable-next-line no-unused-vars
export function fetchSingleModerationEvent(moderationID) {
    return async dispatch => {
        dispatch(startFetchingSingleModerationEvent());
        // TODO: Replace the mock implementation with an actual API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1347
        return new Promise(resolve => {
            setTimeout(() => resolve({ data: eventMockData }), 1000);
        })
            .then(({ data }) =>
                dispatch(completeFetchingSingleModerationEvent(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation event',
                        failFetchingSingleModerationEvent,
                    ),
                ),
            );
    };
}

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
