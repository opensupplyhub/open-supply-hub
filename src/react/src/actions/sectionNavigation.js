import { createAction } from 'redux-act';

export const setScrollTargetSection = createAction('SET_SCROLL_TARGET_SECTION');
export const clearScrollTargetSection = createAction(
    'CLEAR_SCROLL_TARGET_SECTION',
);
export const toggleSectionOpen = createAction('TOGGLE_SECTION_OPEN');
export const resetSectionNavigation = createAction('RESET_SECTION_NAVIGATION');
