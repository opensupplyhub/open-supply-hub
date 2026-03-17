import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    setScrollTargetSection,
    clearScrollTargetSection,
    toggleSectionOpen,
} from '../actions/sectionNavigation';

const initialState = Object.freeze({
    scrollTargetId: null,
    openSectionIds: {},
});

export default createReducer(
    {
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
