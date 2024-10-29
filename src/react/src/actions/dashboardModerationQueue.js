import { createAction } from 'redux-act';
import {
    logErrorAndDispatchFailure,
    downloadModerationEventsXLSX,
} from '../util/util';

export const startFetchingModerationEvents = createAction(
    'START_FETCHING_MODERATION_EVENTS',
);
export const failFetchingModerationEvents = createAction(
    'FAIL_FETCHING_MODERATION_EVENTS',
);
export const completeFetchingModerationEvents = createAction(
    'COMPLETE_FETCHING_MODERATION_EVENTS',
);
export const startDownloadingModerationEvents = createAction(
    'START_DOWNLOADING_MODERATION_EVENTS',
);
export const failDownloadingModerationEvents = createAction(
    'FAIL_DOWNLOADING_MODERATION_EVENTS',
);
export const completeDownloadingModerationEvents = createAction(
    'COMPLETE_DOWNLOADING_MODERATION_EVENTS',
);

// TODO: Remove mock data and replace with actual API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1175
const mockData = [
    {
        moderation_id: 1,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Generic Soft Inc',
        country: {
            name: 'United States',
            alpha_2: 'US',
            alpha_3: 'USA',
            numeric: '840',
        },
        contributor_name: 'International Business Machines',
        moderation_status: 'RESOLVED',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
        source: 'API',
    },
    {
        moderation_id: 2,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Sporting Goods Manufacturer',
        country: {
            name: 'United States',
            alpha_2: 'US',
            alpha_3: 'USA',
            numeric: '840',
        },
        contributor_name: 'General Services',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
        source: 'SLC',
    },
    {
        moderation_id: 3,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Printing materials factory',
        country: {
            name: 'Italy',
            alpha_2: 'IT',
            alpha_3: 'ITA',
            numeric: '380',
        },
        contributor_name: 'Global Printing',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
        source: 'API',
    },
    {
        moderation_id: 4,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Textile Machinery',
        country: {
            name: 'Canada',
            alpha_2: 'CA',
            alpha_3: 'CAN',
            numeric: '124',
        },
        contributor_name: 'International Business Machines',
        moderation_status: 'RESOLVED',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
        source: 'SLC',
    },
    {
        moderation_id: 5,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Sporting Goods and Equipment Inc',
        country: {
            name: 'United States',
            alpha_2: 'US',
            alpha_3: 'USA',
            numeric: '840',
        },
        contributor_name: 'Sport Services',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
        source: 'API',
    },
    {
        moderation_id: 6,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Printing materials factory',
        country: {
            name: 'Italy',
            alpha_2: 'IT',
            alpha_3: 'ITA',
            numeric: '380',
        },
        contributor_name: 'Global Printing',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
        source: 'SLC',
    },
];

export function fetchModerationEvents() {
    return async dispatch => {
        dispatch(startFetchingModerationEvents());

        // TODO: Replace the mock implementation with an actual API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1175
        return new Promise(resolve => {
            setTimeout(() => resolve({ data: mockData }), 1000);
        })
            .then(({ data }) =>
                dispatch(completeFetchingModerationEvents(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching moderation events',
                        failFetchingModerationEvents,
                    ),
                ),
            );
    };
}

export function downloadModerationEvents(data) {
    return dispatch => {
        dispatch(startDownloadingModerationEvents());

        try {
            downloadModerationEventsXLSX(data);
            dispatch(completeDownloadingModerationEvents());
        } catch (err) {
            dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented downloading moderation events',
                    failDownloadingModerationEvents,
                ),
            );
        }
    };
}
