import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import { logErrorAndDispatchFailure } from '../util/util';

export const startFetchPartnerFieldGroups = createAction(
    'START_FETCH_PARTNER_FIELD_GROUPS',
);
export const failFetchPartnerFieldGroups = createAction(
    'FAIL_FETCH_PARTNER_FIELD_GROUPS',
);
export const completeFetchPartnerFieldGroups = createAction(
    'COMPLETE_FETCH_PARTNER_FIELD_GROUPS',
);

export const setScrollTargetSection = createAction('SET_SCROLL_TARGET_SECTION');
export const clearScrollTargetSection = createAction(
    'CLEAR_SCROLL_TARGET_SECTION',
);
export const toggleSectionOpen = createAction('TOGGLE_SECTION_OPEN');

const fetchURL = '/api/partner-field-groups/?limit=100';

export function fetchPartnerFieldGroups() {
    return dispatch => {
        dispatch(startFetchPartnerFieldGroups());

        return apiRequest
            .get(fetchURL)
            .then(({ data }) => dispatch(completeFetchPartnerFieldGroups(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching partner field groups',
                        failFetchPartnerFieldGroups,
                    ),
                ),
            );
    };
}
