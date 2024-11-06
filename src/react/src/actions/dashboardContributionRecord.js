import { createAction } from 'redux-act';
import { logErrorAndDispatchFailure } from '../util/util';

export const startFetchingModerationEvent = createAction(
    'START_FETCHING_MODERATION_EVENT',
);
export const failFetchingModerationEvent = createAction(
    'FAIL_FETCHING_MODERATION_EVENT',
);
export const completeFetchingModerationEvent = createAction(
    'COMPLETE_FETCHING_MODERATION_EVENT',
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

// TODO: Remove mock data and replace with actual API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1347
const eventMockData = {
    moderation_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    created_at: '2024-10-17T11:30:20.287Z',
    updated_at: '2024-10-18T11:30:20.287Z',
    os_id: 'CN2021250D1DTN7',
    cleaned_data: {
        name: 'Eco Friendly Plastics',
        address: '435 Main St, Manhattan, NY - USA',
        country: {
            name: 'Germany',
            alpha_2: 'DE',
            alpha_3: 'DEU',
            numeric: '276',
        },
    },
    contributor_id: 0,
    contributor_name: 'Green Solutions Corp',
    request_type: 'CREATE',
    source: 'API',
    moderation_status: 'PENDING',
    moderation_decision_date: null,
    claim_id: 0,
};

// TODO: Remove mock data and replace with actual API call as part  of /v1/production-locations endpoint
const potentialMatchesMockData = [
    {
        os_id: 'CN2021250D1DTN7',
        name: 'Test name INC',
        address: '435 Main St, Manhattan, NY - USA',
        sector: ['Apparel'],
        parent_company: 'ASI GLOBAL LIMITED',
        product_type: ['Accessories'],
        location_type: [],
        processing_type: ['Final Product Assembly'],
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
export function fetchModerationEvent(moderationID) {
    return async dispatch => {
        dispatch(startFetchingModerationEvent());

        // TODO: Replace the mock implementation with an actual API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1347
        return new Promise(resolve => {
            setTimeout(() => resolve({ data: eventMockData }), 1000);
        })
            .then(({ data }) => dispatch(completeFetchingModerationEvent(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation event',
                        failFetchingModerationEvent,
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
