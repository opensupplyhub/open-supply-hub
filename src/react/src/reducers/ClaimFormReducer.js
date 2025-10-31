import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
    resetClaimForm,
    startSubmitClaimFormData,
    failSubmitClaimFormData,
    completeSubmitClaimFormData,
} from '../actions/claimForm';

const initialState = Object.freeze({
    activeStep: 0,
    completedSteps: [],
    formData: Object.freeze({
        // Eligibility step.
        relationship: null,

        // Contact step.
        contactEmail: '',
        contactPhone: '',
        yourBusinessWebsite: '',

        // Business step.
        locationAddressVerificationMethod: '',
        businessLinkedinProfile: '',
        businessWebsite: '',
        companyAddressVerificationDocuments: [],

        // Profile step - Production Location Overview.
        localLanguageName: '',
        officePhoneNumber: '',
        facilityDescription: '',

        // Profile step - Company Information.
        parentCompanyName: '',
        officeOfficialName: '',
        officeAddress: '',
        officeCountryCode: '',

        // Profile step - Operations & Capabilities.
        sectors: [],
        facilityType: [],
        facilityProductionTypes: [],
        facilityProductTypes: [],
        numberOfWorkers: '',
        facilityFemaleWorkersPercentage: '',
        facilityMinimumOrderQuantity: '',
        facilityAverageLeadTime: '',

        // Profile step - Compliance & Partnerships.
        facilityAffiliations: [],
        facilityCertifications: [],

        // Profile step - Free Emissions Estimate.
        openingDate: '',
        closingDate: '',
        estimatedAnnualThroughput: '',
        energyCoal: '',
        energyNaturalGas: '',
        energyDiesel: '',
        energyKerosene: '',
        energyBiomass: '',
        energyCharcoal: '',
        energyAnimalWaste: '',
        energyElectricity: '',
        energyOther: '',
        energyCoalEnabled: false,
        energyNaturalGasEnabled: false,
        energyDieselEnabled: false,
        energyKeroseneEnabled: false,
        energyBiomassEnabled: false,
        energyCharcoalEnabled: false,
        energyAnimalWasteEnabled: false,
        energyElectricityEnabled: false,
        energyOtherEnabled: false,
    }),
    submissionState: Object.freeze({
        fetching: false,
        error: null,
        data: null,
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

        [startSubmitClaimFormData]: state =>
            update(state, {
                submissionState: {
                    fetching: { $set: true },
                    error: { $set: null },
                    data: { $set: null },
                },
            }),

        [failSubmitClaimFormData]: (state, error) =>
            update(state, {
                submissionState: {
                    fetching: { $set: false },
                    error: { $set: error },
                },
            }),

        [completeSubmitClaimFormData]: (state, data) =>
            update(state, {
                submissionState: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: data },
                },
            }),
    },
    initialState,
);

export default claimFormReducer;
