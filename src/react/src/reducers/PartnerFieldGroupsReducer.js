import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchPartnerFieldGroups,
    failFetchPartnerFieldGroups,
    completeFetchPartnerFieldGroups,
    setScrollTargetSection,
    clearScrollTargetSection,
    toggleSectionOpen,
} from '../actions/partnerFieldGroups';

const initialState = Object.freeze({
    fetching: false,
    data: null,
    error: null,
    scrollTargetId: null,
    openSectionIds: {},
});

export default createReducer(
    {
        [startFetchPartnerFieldGroups]: state =>
            update(state, {
                fetching: { $set: true },
                error: { $set: null },
            }),
        [failFetchPartnerFieldGroups]: (state, error) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: error },
            }),
        [completeFetchPartnerFieldGroups]: (state, data) =>
            Object.freeze(
                update(state, {
                    fetching: { $set: false },
                    data: { $set: data },
                }),
            ),
        [setScrollTargetSection]: (state, scrollTargetId) =>
            update(state, {
                scrollTargetId: { $set: scrollTargetId },
                openSectionIds: { [scrollTargetId]: { $set: true } },
            }),
        [clearScrollTargetSection]: state =>
            update(state, { scrollTargetId: { $set: null } }),
        [toggleSectionOpen]: (state, uuid) =>
            update(state, {
                openSectionIds: {
                    [uuid]: { $set: !state.openSectionIds[uuid] },
                },
            }),
    },
    initialState,
);
