import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
    resetClaimForm,
} from '../actions/claimForm';

const initialState = Object.freeze({
    activeStep: 0,
    completedSteps: [],
    formData: Object.freeze({
        // Eligibility step.
        relationship: null,

        // Contact step.
        claimantName: '',
        claimantTitle: '',
        contactEmail: null,
        contactPhone: '',
        employmentVerification: null,
        employmentVerificationUrl: '',
        employmentVerificationFiles: null,

        // Business step.
        locationAddressVerificationMethod: '',
        businessLinkedinProfile: '',
        businessWebsite: '',
        companyAddressVerificationDocuments: [],

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

        [resetClaimForm]: () => initialState,
    },
    initialState,
);

export default claimFormReducer;
