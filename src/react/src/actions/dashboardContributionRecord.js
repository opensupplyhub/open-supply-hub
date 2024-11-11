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
    moderation_id: 12,
    created_at: '2024-06-13T15:30:20.287Z',
    updated_at: '2024-09-20T11:35:20.287Z',
    os_id: 'FN2071250D1DTN7',
    cleaned_data: {
        name: 'Eco Test Friendly Plastics',
        address: '4999 Main St, Manhattan, NY - USA',
        country: {
            name: 'Germany',
            alpha_2: 'DE',
            alpha_3: 'DEU',
            numeric: '276',
        },
    },
    contributor_id: 0,
    contributor_name: 'Green Test Solutions Corp',
    request_type: 'CREATE',
    source: 'API',
    moderation_status: 'PENDING',
    moderation_decision_date: null,
    claim_id: 0,
};
// TODO: Remove mock data and replace with actual API call as part  of /v1/production-locations endpoint
const potentialMatchesMockData = [
    {
        os_id: 'CY2021280D1DTN7',
        name: 'Test name INC NEW',
        address: '1523 Main St, Manhattan, NY - USA',
        sector: ['Apparel'],
        parent_company: 'ASI TEST GLOBAL LIMITED',
        product_type: ['Accessories'],
        location_type: [],
        processing_type: ['Product Assembly'],
        number_of_workers: {
            min: 0,
            max: 0,
        },
        coordinates: {
            lat: 0,
            lng: 0,
        },
        local_name: '',
        description: '',
        business_url: '',
        minimum_order_quantity: '',
        average_lead_time: '',
        percent_female_workers: 0,
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
