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
import { dismissedWarningsFor } from '../util/claimQualityCheck';

// Step navigation actions.
export const setActiveClaimFormStep = createAction(
    'SET_ACTIVE_CLAIM_FORM_STEP',
);
export const markStepComplete = createAction('MARK_CLAIM_FORM_STEP_COMPLETE');

// Form data actions.
export const updateClaimFormField = createAction('UPDATE_CLAIM_FORM_FIELD');
export const resetClaimForm = createAction('RESET_CLAIM_FORM');
export const updateOsIdToClaim = createAction('UPDATE_OS_ID_TO_CLAIM');

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
export const clearClaimFormSubmissionError = createAction(
    'CLEAR_CLAIM_FORM_SUBMISSION_ERROR',
);

const makeClaimFacilityAPIURL = osID => `/api/facilities/${osID}/claim/`;

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

    const formattedKey = snakeCase(key);

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

        // The quality-check dismissal is form state, not a claim field:
        // it is reported separately, and only while it still applies to
        // the name and address being submitted (OSDEV-3489).
        const {
            qualityWarningsDismissed,
            ...filteredFormData
        } = filterFreeEmissionsEstimateFields(formData);

        const postData = new FormData();
        toPairs(filteredFormData).forEach(([key, value]) => {
            appendFormField(postData, key, value);
        });
        const dismissedWarnings = dismissedWarningsFor(
            {
                name: formData.facilityNameEnglish,
                address: formData.facilityAddress,
            },
            qualityWarningsDismissed,
        );
        if (dismissedWarnings.length > 0) {
            postData.append(
                'dismissed_warnings',
                JSON.stringify(dismissedWarnings),
            );
        }

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
