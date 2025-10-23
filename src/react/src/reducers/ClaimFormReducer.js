import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
    setClaimFormData,
    resetClaimForm,
} from '../actions/claimForm';

const initialState = Object.freeze({
    activeStep: 0,
    completedSteps: [],
    formData: Object.freeze({
        // Eligibility step.
        position: '',
        yearsAtCompany: '',

        // Contact step.
        contactEmail: '',
        contactPhone: '',

        // Business step.
        businessName: '',
        businessWebsite: '',

        // Profile step.
        numberOfWorkers: '',
        additionalNotes: '',
    }),
});

const claimFormReducer = createReducer(
    {
        [setActiveClaimFormStep]: (state, stepIndex) =>
            update(state, {
                activeStep: { $set: stepIndex },
            }),

        [markStepComplete]: (state, stepIndex) => {
            const completedSteps = state.completedSteps.includes(stepIndex)
                ? state.completedSteps
                : [...state.completedSteps, stepIndex];

            return update(state, {
                completedSteps: { $set: completedSteps },
            });
        },

        [updateClaimFormField]: (state, { field, value }) =>
            update(state, {
                formData: {
                    [field]: { $set: value },
                },
            }),

        [setClaimFormData]: (state, formData) =>
            update(state, {
                formData: { $set: formData },
            }),

        [resetClaimForm]: () => initialState,
    },
    initialState,
);

export default claimFormReducer;
