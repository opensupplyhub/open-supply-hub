import { createAction } from 'redux-act';
import { snakeCase, toPairs } from 'lodash';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    filterFreeEmissionsEstimateFields,
    appendFiles,
    appendArrayField,
    appendFacilityType,
    appendSimpleField,
} from '../util/util';

// Step navigation actions.
export const setActiveClaimFormStep = createAction(
    'SET_ACTIVE_CLAIM_FORM_STEP',
);
export const markStepComplete = createAction('MARK_CLAIM_FORM_STEP_COMPLETE');

// Form data actions.
export const updateClaimFormField = createAction('UPDATE_CLAIM_FORM_FIELD');
export const resetClaimForm = createAction('RESET_CLAIM_FORM');

// Submission actions.
export const startSubmitClaimFormData = createAction(
    'START_SUBMIT_CLAIM_FORM_DATA',
);
export const failSubmitClaimFormData = createAction(
    'FAIL_SUBMIT_CLAIM_FORM_DATA',
);
export const completeSubmitClaimFormData = createAction(
    'COMPLETE_SUBMIT_CLAIM_FORM_DATA',
);

const makeClaimFacilityAPIURL = osID => `/api/facilities/${osID}/claim/`;

/**
 * Temporary transform field name to API format.
 * Remove once proper form fields names are implemented.
 */
const mapFieldNameToAPI = key => {
    const specialMappings = {
        relationship: 'claimant_location_relationship',
        contactEmail: 'point_of_contact_email',
    };

    return specialMappings[key] || snakeCase(key);
};

/**
 * Add temporary mock values for required fields.
 * Remove once proper form fields are implemented.
 */
const addMockRequiredFields = postData => {
    if (!postData.has('your_name')) {
        postData.append('your_name', 'Test Claimant Name');
    }
    if (!postData.has('your_title')) {
        postData.append('your_title', 'Test Title');
    }
};

const appendFormField = (postData, key, value) => {
    const arrayFieldsKeys = [
        'sectors',
        'facility_production_types',
        'facility_product_types',
        'facility_affiliations',
        'facility_certifications',
    ];

    const fileFieldsKeys = [
        'company_address_verification_documents',
        'employment_verification_documents',
    ];

    const formattedKey = mapFieldNameToAPI(key);

    if (fileFieldsKeys.includes(formattedKey)) {
        appendFiles(postData, 'files', value);
    } else if (arrayFieldsKeys.includes(formattedKey)) {
        appendArrayField(postData, formattedKey, value);
    } else if (formattedKey === 'facility_type') {
        appendFacilityType(postData, formattedKey, value);
    } else {
        appendSimpleField(postData, formattedKey, value);
    }
};

export function submitClaimFormData(osID, freeEmissionsEstimateHasErrors) {
    return (dispatch, getState) => {
        const {
            claimForm: { formData },
        } = getState();

        if (freeEmissionsEstimateHasErrors) {
            return null;
        }

        const filteredFormData = filterFreeEmissionsEstimateFields(formData);

        const postData = new FormData();
        toPairs(filteredFormData).forEach(([key, value]) => {
            appendFormField(postData, key, value);
        });

        addMockRequiredFields(postData);

        dispatch(startSubmitClaimFormData());

        return apiRequest
            .post(makeClaimFacilityAPIURL(osID), postData)
            .then(({ data }) => {
                dispatch(completeSubmitClaimFormData(data));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented submitting claim data',
                        failSubmitClaimFormData,
                    ),
                ),
            );
    };
}
