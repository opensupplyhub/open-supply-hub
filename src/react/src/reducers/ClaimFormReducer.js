import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startPrefetchClaimFormData,
    completePrefetchClaimFormData,
    failPrefetchClaimFormData,
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
        // Eligibility step
        eligibilityConfirmed: false,

        // Contact step
        claimantName: '',
        claimantTitle: '',
        claimantEmail: '',
        verificationMethod: '',
        contactName: '',
        contactEmail: '',

        // Business step
        businessWebsite: '',
        companyAddressVerification: '',

        // Profile step
        facilityName: '',
        sector: [],
        facilityPhone: '',
        facilityWebsite: '',
        localLanguageName: '',
        numberOfWorkers: '',
        femaleWorkers: '',
        minimumOrderQuantity: '',
        averageLeadTime: '',
        facilityTypes: [],
        productTypes: '',
        parentCompanyName: '',
        officeName: '',
        officeAddress: '',
        officeCountry: '',
        affiliations: [],
        certifications: [],
        description: '',
    }),
    prefetchedData: Object.freeze({
        sectors: [],
        processingTypes: [],
        affiliations: [],
        certifications: [],
        facilityData: null,
    }),
    fetching: false,
    error: null,
});

const claimFormReducer = createReducer(
    {
        [startPrefetchClaimFormData]: state =>
            update(state, {
                fetching: { $set: true },
                error: { $set: null },
            }),

        [completePrefetchClaimFormData]: (state, payload) =>
            update(state, {
                fetching: { $set: false },
                prefetchedData: { $set: payload },
                error: { $set: null },
            }),

        [failPrefetchClaimFormData]: (state, payload) =>
            update(state, {
                fetching: { $set: false },
                error: { $set: payload },
            }),

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
