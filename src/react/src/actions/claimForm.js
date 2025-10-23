import { createAction } from 'redux-act';

// Step navigation actions.
export const setActiveClaimFormStep = createAction(
    'SET_ACTIVE_CLAIM_FORM_STEP',
);
export const markStepComplete = createAction('MARK_CLAIM_FORM_STEP_COMPLETE');

// Form data actions.
export const updateClaimFormField = createAction('UPDATE_CLAIM_FORM_FIELD');
export const setClaimFormData = createAction('SET_CLAIM_FORM_DATA');
export const resetClaimForm = createAction('RESET_CLAIM_FORM');
