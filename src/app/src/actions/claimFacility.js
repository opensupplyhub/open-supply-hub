import { createAction } from 'redux-act';
import get from 'lodash/get';
import snakeCase from 'lodash/snakeCase';
import mapKeys from 'lodash/mapKeys';

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

export const updateClaimAFacilityContactPerson = createAction(
    'UPDATE_CLAIM_A_FACILITY_CONTACT_PERSON',
);
export const updateClaimAFacilityJobTitle = createAction(
    'UPDATE_CLAIM_A_FACILITY_JOB_TITLE',
);
export const updateClaimAFacilityEmail = createAction(
    'UPDATE_CLAIM_A_FACILITY_EMAIL',
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
export const updateClaimAFacilityPreferredContactMethod = createAction(
    'UPDATE_CLAIM_A_FACILITY_PREFERRED_CONTACT_METHOD',
);
export const updateClaimAFacilityLinkedinProfile = createAction(
    'UPDATE_CLAIM_A_FACILITY_LINKEDIN_PROFILE',
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

        const postData = mapKeys(
            Object.assign({}, formData, {
                preferredContactMethod: get(
                    formData,
                    'preferredContactMethod.value',
                    null,
                ),
                parentCompany: get(formData, 'parentCompany.value', null),
            }),
            (_, k) => snakeCase(k),
        );

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
