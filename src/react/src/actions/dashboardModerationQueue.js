import { createAction } from 'redux-act';

import { logErrorAndDispatchFailure } from '../util/util';

export const startFetchingModerationEvents = createAction(
    'START_FETCHING_MODERATION_EVENTS',
);
export const failFetchingModerationEvents = createAction(
    'FAIL_FETCHING_MODERATION_EVENTS',
);
export const completeFetchingModerationEvents = createAction(
    'COMPLETE_FETCHING_MODERATION_EVENTS',
);

const mockData = [
    {
        moderation_id: 1,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Generic Soft Inc',
        country: {
            name: 'United States',
        },
        contributor_name: 'International Business Machines',
        match_status: 'MATCHED',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
    },
    {
        moderation_id: 2,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Sporting Goods Manufacturer',
        country: {
            name: 'United States',
        },
        contributor_name: 'General Services',
        match_status: 'MATCHED',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
    },
    {
        moderation_id: 3,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Printing materials factory',
        country: {
            name: 'Italy',
        },
        contributor_name: 'Global Printing',
        match_status: 'MATCHED',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
    },
    {
        moderation_id: 4,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Textile Machinery',
        country: {
            name: 'Canada',
        },
        contributor_name: 'International Business Machines',
        match_status: 'MATCHED',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
    },
    {
        moderation_id: 5,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Sporting Goods and Equipment Inc',
        country: {
            name: 'United States',
        },
        contributor_name: 'Sport Services',
        match_status: 'MATCHED',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
    },
    {
        moderation_id: 6,
        created_at: '2024-10-17T10:26:10.277Z',
        name: 'Printing materials factory',
        country: {
            name: 'Italy',
        },
        contributor_name: 'Global Printing',
        match_status: 'MATCHED',
        moderation_status: 'PENDING',
        moderation_decision_date: '2024-10-17T10:26:10.277Z',
        updated_at: '2024-10-17T10:26:10.277Z',
    },
];

export function fetchModerationEvents() {
    return async dispatch => {
        dispatch(startFetchingModerationEvents());

        // TODO: replace with actual API call during implementation OSDEV-1175
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
