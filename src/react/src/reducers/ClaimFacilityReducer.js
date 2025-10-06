import { createReducer } from 'redux-act';
import update from 'immutability-helper';
import identity from 'lodash/identity';
import orderBy from 'lodash/orderBy';

import {
    updateClaimFacilityIntro,
    startFetchClaimFacilityData,
    failFetchClaimFacilityData,
    completeFetchClaimFacilityData,
    clearClaimFacilityDataAndForm,
    updateClaimAFacilityYourName,
    updateClaimAFacilityYourTitle,
    updateClaimAFacilityYourBusinessWebsite,
    updateClaimAFacilityBusinessWebsite,
    updateClaimAFacilityBusinessLinkedinProfile,
    updateClaimASector,
    updateClaimANumberOfWorkers,
    updateClaimALocalLanguageName,
    startSubmitClaimAFacilityData,
    failSubmitClaimAFacilityData,
    completeSubmitClaimAFacilityData,
    updateClaimAFacilityUploadFiles,
    updateClaimAFacilityBusinessUploadFiles,
    updateClaimOpeningDate,
    updateClaimClosingDate,
    updateClaimEstimatedAnnualThroughput,
    updateClaimEnergyCoal,
    updateClaimEnergyNaturalGas,
    updateClaimEnergyDiesel,
    updateClaimEnergyKerosene,
    updateClaimEnergyBiomass,
    updateClaimEnergyCharcoal,
    updateClaimEnergyAnimalWaste,
    updateClaimEnergyElectricity,
    updateClaimEnergyOther,
    updateClaimEnergyCoalEnabled,
    updateClaimEnergyNaturalGasEnabled,
    updateClaimEnergyDieselEnabled,
    updateClaimEnergyKeroseneEnabled,
    updateClaimEnergyBiomassEnabled,
    updateClaimEnergyCharcoalEnabled,
    updateClaimEnergyAnimalWasteEnabled,
    updateClaimEnergyElectricityEnabled,
    updateClaimEnergyOtherEnabled,
} from '../actions/claimFacility';

/**
 * Helper function to set a form field for the free
 * emissions estimate fields.
 */
const setFormField = key => (state, payload) =>
    update(state, {
        claimData: {
            formData: {
                [key]: { $set: payload },
            },
        },
    });

const FREE_EMISSIONS_FIELDS = [
    [updateClaimOpeningDate, 'openingDate'],
    [updateClaimClosingDate, 'closingDate'],
    [updateClaimEstimatedAnnualThroughput, 'estimatedAnnualThroughput'],
    [updateClaimEnergyCoal, 'energyCoal'],
    [updateClaimEnergyNaturalGas, 'energyNaturalGas'],
    [updateClaimEnergyDiesel, 'energyDiesel'],
    [updateClaimEnergyKerosene, 'energyKerosene'],
    [updateClaimEnergyBiomass, 'energyBiomass'],
    [updateClaimEnergyCharcoal, 'energyCharcoal'],
    [updateClaimEnergyAnimalWaste, 'energyAnimalWaste'],
    [updateClaimEnergyElectricity, 'energyElectricity'],
    [updateClaimEnergyOther, 'energyOther'],
    [updateClaimEnergyCoalEnabled, 'energyCoalEnabled'],
    [updateClaimEnergyNaturalGasEnabled, 'energyNaturalGasEnabled'],
    [updateClaimEnergyDieselEnabled, 'energyDieselEnabled'],
    [updateClaimEnergyKeroseneEnabled, 'energyKeroseneEnabled'],
    [updateClaimEnergyBiomassEnabled, 'energyBiomassEnabled'],
    [updateClaimEnergyCharcoalEnabled, 'energyCharcoalEnabled'],
    [updateClaimEnergyAnimalWasteEnabled, 'energyAnimalWasteEnabled'],
    [updateClaimEnergyElectricityEnabled, 'energyElectricityEnabled'],
    [updateClaimEnergyOtherEnabled, 'energyOtherEnabled'],
];

const freeEmissionsReducers = Object.fromEntries(
    FREE_EMISSIONS_FIELDS.map(([action, key]) => [action, setFormField(key)]),
);

const initialState = Object.freeze({
    facilityData: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    claimData: Object.freeze({
        formData: Object.freeze({
            yourName: '',
            yourTitle: '',
            yourBusinessWebsite: '',
            businessWebsite: '',
            businessLinkedinProfile: '',
            sectors: null,
            numberOfWorkers: '',
            localLanguageName: '',
            agreement: 'no',
            // Free Emissions Estimate fields
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
        fetching: false,
        error: null,
    }),
    parentCompanyOptions: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [updateClaimFacilityIntro]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        agreement: { $set: payload },
                    },
                },
            }),
        [startFetchClaimFacilityData]: state =>
            update(state, {
                facilityData: {
                    data: { $set: initialState.facilityData.data },
                    fetching: { $set: true },
                    error: { $set: initialState.facilityData.error },
                },
            }),
        [failFetchClaimFacilityData]: (state, error) =>
            update(state, {
                facilityData: {
                    fetching: { $set: false },
                    error: { $set: error },
                },
            }),
        [completeFetchClaimFacilityData]: (state, data) =>
            update(state, {
                facilityData: {
                    data: { $set: data },
                    fetching: { $set: false },
                    error: { $set: initialState.facilityData.error },
                },
            }),
        [updateClaimAFacilityYourName]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        yourName: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityYourTitle]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        yourTitle: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityYourBusinessWebsite]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        yourBusinessWebsite: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityBusinessWebsite]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        businessWebsite: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityBusinessLinkedinProfile]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        businessLinkedinProfile: { $set: payload },
                    },
                },
            }),
        [updateClaimASector]: (state, sectors) =>
            update(state, {
                claimData: {
                    formData: {
                        sectors: {
                            $set: orderBy(sectors, identity),
                        },
                    },
                },
            }),
        [updateClaimANumberOfWorkers]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        numberOfWorkers: { $set: payload },
                    },
                },
            }),
        [updateClaimALocalLanguageName]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        localLanguageName: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityUploadFiles]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        uploadFiles: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityBusinessUploadFiles]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        businessUploadFiles: { $set: payload },
                    },
                },
            }),
        [startSubmitClaimAFacilityData]: state =>
            update(state, {
                claimData: {
                    error: { $set: initialState.claimData.error },
                    fetching: { $set: true },
                },
            }),
        [failSubmitClaimAFacilityData]: (state, error) =>
            update(state, {
                claimData: {
                    error: { $set: error },
                    fetching: { $set: false },
                },
            }),
        [completeSubmitClaimAFacilityData]: state =>
            update(state, {
                claimData: {
                    fetching: { $set: false },
                },
            }),
        ...freeEmissionsReducers,
        [clearClaimFacilityDataAndForm]: () => initialState,
    },
    initialState,
);
