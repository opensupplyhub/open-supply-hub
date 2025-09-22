import { createAction } from 'redux-act';
import { toPairs, snakeCase, mapKeys } from 'lodash';

import apiRequest from '../util/apiRequest';

import {
    logErrorAndDispatchFailure,
    makeGetFacilityByOSIdURL,
    makeClaimFacilityAPIURL,
    claimAFacilityFormIsValid,
} from '../util/util';

export const startFetchClaimFacilityData = createAction(
    'START_FETCH_CLAIM_FACILITY_DATA',
);
export const failFetchClaimFacilityData = createAction(
    'FAIL_FETCH_CLAIM_FACILITY_DATA',
);
export const completeFetchClaimFacilityData = createAction(
    'COMPLETE_FETCH_CLAIM_FACILITY_DATA',
);
export const clearClaimFacilityDataAndForm = createAction(
    'CLEAR_CLAIM_FACILITY_DATA_AND_FORM',
);

export function fetchClaimFacilityData(osID) {
    return dispatch => {
        dispatch(startFetchClaimFacilityData());

        return apiRequest
            .get(makeGetFacilityByOSIdURL(osID))
            .then(({ data }) => dispatch(completeFetchClaimFacilityData(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching data about that facility',
                        failFetchClaimFacilityData,
                    ),
                ),
            );
    };
}

export const updateClaimFacilityIntro = createAction(
    'UPDATE_CLAIM_A_FACILITY_INTRO',
);

export const updateClaimAFacilityContactPerson = createAction(
    'UPDATE_CLAIM_A_FACILITY_CONTACT_PERSON',
);
export const updateClaimAFacilityJobTitle = createAction(
    'UPDATE_CLAIM_A_FACILITY_JOB_TITLE',
);
export const updateClaimAFacilityPhoneNumber = createAction(
    'UPDATE_CLAIM_A_FACILITY_PHONE_NUMBER',
);
export const updateClaimAFacilityCompany = createAction(
    'UPDATE_CLAIM_A_FACILITY_COMPANY',
);
export const updateClaimAFacilityParentCompany = createAction(
    'UPDATE_CLAIM_A_FACILITY_PARENT_COMPANY',
);
export const updateClaimAFacilityWebsite = createAction(
    'UPDATE_CLAIM_A_FACILITY_WEBSITE',
);
export const updateClaimAFacilityDescription = createAction(
    'UPDATE_CLAIM_A_FACILITY_DESCRIPTION',
);
export const updateClaimAFacilityVerificationMethod = createAction(
    'UPDATE_CLAIM_A_FACILITY_VERIFICATION_METHOD',
);
export const updateClaimAFacilityLinkedinProfile = createAction(
    'UPDATE_CLAIM_A_FACILITY_LINKEDIN_PROFILE',
);
export const updateClaimAFacilityUploadFiles = createAction(
    'UPDATE_CLAIM_A_FACILITY_UPLOAD_FILES',
);
export const updateClaimAFacilityBusinessUploadFiles = createAction(
    'UPDATE_CLAIM_A_FACILITY_BUSINESS_UPLOAD_FILES',
);
export const startSubmitClaimAFacilityData = createAction(
    'START_SUBMIT_CLAIM_A_FACILITY_DATA',
);
export const failSubmitClaimAFacilityData = createAction(
    'FAIL_SUBMIT_CLAIM_A_FACILITY_DATA',
);
export const completeSubmitClaimAFacilityData = createAction(
    'COMPLETE_SUBMIT_CLAIM_A_FACILITY_DATA',
);
export const updateClaimAFacilityYourName = createAction(
    'UPDATE_CLAIM_A_FACILITY_YOUR_NAME',
);
export const updateClaimAFacilityYourTitle = createAction(
    'UPDATE_CLAIM_A_FACILITY_YOUR_TITLE',
);
export const updateClaimAFacilityYourBusinessWebsite = createAction(
    'UPDATE_CLAIM_A_FACILITY_YOUR_BUSINESS_WEBSITE',
);
export const updateClaimAFacilityBusinessWebsite = createAction(
    'UPDATE_CLAIM_A_FACILITY_BUSINESS_WEBSITE',
);
export const updateClaimAFacilityBusinessLinkedinProfile = createAction(
    'UPDATE_CLAIM_A_FACILITY_YOUR_BUSINESS_LINKEDIN_PROFILE',
);

export const updateClaimASector = createAction('UPDATE_CLAIM_A_SECTOR');
export const updateClaimANumberOfWorkers = createAction(
    'UPDATE_CLAIM_A_NUMBER_OF_WORKERS',
);
export const updateClaimALocalLanguageName = createAction(
    'UPDATE_CLAIM_A_LOCAL_LANGUAGE_NAME',
);

// Free Emissions Estimate actions
export const updateClaimOpeningDate = createAction('UPDATE_CLAIM_OPENING_DATE');
export const updateClaimClosingDate = createAction('UPDATE_CLAIM_CLOSING_DATE');
export const updateClaimAnnualThroughput = createAction(
    'UPDATE_CLAIM_ANNUAL_THROUGHPUT',
);
export const updateClaimEnergyCoal = createAction('UPDATE_CLAIM_ENERGY_COAL');
export const updateClaimEnergyNaturalGas = createAction(
    'UPDATE_CLAIM_ENERGY_NATURAL_GAS',
);
export const updateClaimEnergyDiesel = createAction(
    'UPDATE_CLAIM_ENERGY_DIESEL',
);
export const updateClaimEnergyKerosene = createAction(
    'UPDATE_CLAIM_ENERGY_KEROSENE',
);
export const updateClaimEnergyBiomass = createAction(
    'UPDATE_CLAIM_ENERGY_BIOMASS',
);
export const updateClaimEnergyCharcoal = createAction(
    'UPDATE_CLAIM_ENERGY_CHARCOAL',
);
export const updateClaimEnergyAnimalWaste = createAction(
    'UPDATE_CLAIM_ENERGY_ANIMAL_WASTE',
);
export const updateClaimEnergyElectricity = createAction(
    'UPDATE_CLAIM_ENERGY_ELECTRICITY',
);
export const updateClaimEnergyOther = createAction('UPDATE_CLAIM_ENERGY_OTHER');
export const updateClaimEnergyCoalEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_COAL_ENABLED',
);
export const updateClaimEnergyNaturalGasEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_NATURAL_GAS_ENABLED',
);
export const updateClaimEnergyDieselEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_DIESEL_ENABLED',
);
export const updateClaimEnergyKeroseneEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_KEROSENE_ENABLED',
);
export const updateClaimEnergyBiomassEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_BIOMASS_ENABLED',
);
export const updateClaimEnergyCharcoalEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_CHARCOAL_ENABLED',
);
export const updateClaimEnergyAnimalWasteEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_ANIMAL_WASTE_ENABLED',
);
export const updateClaimEnergyElectricityEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_ELECTRICITY_ENABLED',
);
export const updateClaimEnergyOtherEnabled = createAction(
    'UPDATE_CLAIM_ENERGY_OTHER_ENABLED',
);

export function submitClaimAFacilityData(osID) {
    return (dispatch, getState) => {
        const {
            claimFacility: {
                claimData: { formData },
            },
        } = getState();

        if (!claimAFacilityFormIsValid(formData)) {
            return null;
        }

        const postData = new FormData();
        toPairs(formData).forEach(([key, value]) => {
            const formattedKey = snakeCase(key);
            if (
                formattedKey === 'upload_files' ||
                formattedKey === 'business_upload_files'
            ) {
                mapKeys(value, file => {
                    postData.append('files', file);
                });
            } else if (formattedKey === 'sectors') {
                if (value !== null) {
                    postData.append(formattedKey, value);
                }
            } else {
                postData.append(formattedKey, value);
            }
        });

        dispatch(startSubmitClaimAFacilityData());

        return apiRequest
            .post(makeClaimFacilityAPIURL(osID), postData)
            .then(({ data }) =>
                dispatch(completeSubmitClaimAFacilityData(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented submitting facility claim data',
                        failSubmitClaimAFacilityData,
                    ),
                ),
            );
    };
}
