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
        position: '',
        yearsAtCompany: '',

        // Contact step.
        contactEmail: '',
        contactPhone: '',

        // Business step.
        businessName: '',
        businessWebsite: '',

        // Profile step - Production Location Overview.
        localLanguageName: '',
        facilityPhone: '',
        description: '',

        // Profile step - Company Information.
        parentCompanyName: null,
        officeName: '',
        officeAddress: '',
        officeCountry: null,

        // Profile step - Operations & Capabilities.
        sector: [],
        locationType: [],
        processingType: [],
        productTypes: [],
        numberOfWorkers: '',
        femaleWorkers: '',
        minimumOrderQuantity: '',
        averageLeadTime: '',

        // Profile step - Compliance & Partnerships.
        affiliations: [],
        certifications: [],

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
