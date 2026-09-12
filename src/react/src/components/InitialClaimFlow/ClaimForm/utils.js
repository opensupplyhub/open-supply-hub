import camelCase from 'lodash/camelCase';
import isEmpty from 'lodash/isEmpty';
import isString from 'lodash/isString';
import startCase from 'lodash/startCase';
import {
    CLAIM_FORM_API_FIELD_LABELS,
    CLAIM_FORM_STEPS,
    TOTAL_STEPS,
} from './constants';

export const isStepComplete = (stepIndex, completedSteps) =>
    completedSteps.includes(stepIndex);

export const getNextStep = currentStep =>
    Math.min(currentStep + 1, TOTAL_STEPS - 1);

export const getPreviousStep = currentStep => Math.max(currentStep - 1, 0);

export const isFirstStep = stepIndex =>
    stepIndex === CLAIM_FORM_STEPS.ELIGIBILITY;

export const isLastStep = stepIndex => stepIndex === CLAIM_FORM_STEPS.PROFILE;

export const getPrefetchErrorConfig = (errors, handlers) => {
    const {
        countriesError,
        facilityProcessingTypeError,
        parentCompaniesError,
        productionLocationError,
    } = errors;

    const {
        fetchCountries,
        fetchFacilityProcessingType,
        fetchParentCompanies,
        fetchProductionLocation,
        osID,
    } = handlers;

    if (countriesError) {
        return {
            message: 'Failed to load countries data needed for the claim form.',
            onRetry: fetchCountries,
        };
    }

    if (facilityProcessingTypeError) {
        return {
            message:
                'Failed to load facility processing type data needed for the claim form.',
            onRetry: fetchFacilityProcessingType,
        };
    }

    if (parentCompaniesError) {
        return {
            message:
                'Failed to load parent company data needed for the claim form.',
            onRetry: fetchParentCompanies,
        };
    }

    if (productionLocationError) {
        return {
            message:
                'Failed to load production location data needed for the claim form.',
            onRetry: () => fetchProductionLocation(osID),
        };
    }

    return null;
};

// DRF field names are lowercase snake_case / dotted paths.
// Case-sensitive so bare messages like "Error: try again" are not treated as fields.
const isApiFieldPath = fieldPath => {
    if (!fieldPath || fieldPath[0] < 'a' || fieldPath[0] > 'z') {
        return false;
    }

    for (let i = 1; i < fieldPath.length; i += 1) {
        const char = fieldPath[i];
        const isLower = char >= 'a' && char <= 'z';
        const isDigit = char >= '0' && char <= '9';
        if (!isLower && !isDigit && char !== '_' && char !== '.') {
            return false;
        }
    }

    return true;
};

const parseApiFieldErrorMessage = message => {
    const separatorIndex = message.indexOf(': ');
    if (separatorIndex <= 0) {
        return null;
    }

    const fieldPath = message.slice(0, separatorIndex);
    const errorText = message.slice(separatorIndex + 2);
    if (!errorText || !isApiFieldPath(fieldPath)) {
        return null;
    }

    return { fieldPath, errorText };
};

/**
 * Split flattened API error strings into Formik field errors and form-level
 * messages. Expects messages shaped like "field_name: error text" from
 * createErrorListFromResponseObject, or bare strings (e.g. detail).
 */
export const mapSubmissionErrorsToFormFields = errorMessages => {
    const fieldErrors = {};
    const formErrors = [];

    (errorMessages || []).forEach(message => {
        if (!isString(message)) {
            return;
        }

        const parsed = parseApiFieldErrorMessage(message);
        if (!parsed) {
            formErrors.push(message);
            return;
        }

        const { fieldPath, errorText } = parsed;
        const rootField = fieldPath.split('.')[0];

        if (rootField === 'detail' || rootField === 'non_field_errors') {
            formErrors.push(errorText);
            return;
        }

        const formikField = camelCase(rootField);
        if (fieldErrors[formikField]) {
            if (!fieldErrors[formikField].includes(errorText)) {
                fieldErrors[formikField] = [
                    fieldErrors[formikField],
                    errorText,
                ].join('; ');
            }
        } else {
            fieldErrors[formikField] = errorText;
        }
    });

    return { fieldErrors, formErrors };
};

export const getClaimFormFieldLabel = field =>
    CLAIM_FORM_API_FIELD_LABELS[field] || startCase(camelCase(field));

export const formatSubmissionErrorForDisplay = message => {
    if (!isString(message)) {
        return message;
    }

    const parsed = parseApiFieldErrorMessage(message);
    if (!parsed) {
        return message;
    }

    return `${getClaimFormFieldLabel(parsed.fieldPath)}: ${parsed.errorText}`;
};

export const getTouchedFieldsFromErrors = fieldErrors => {
    if (isEmpty(fieldErrors)) {
        return {};
    }

    return Object.keys(fieldErrors).reduce((acc, field) => {
        acc[field] = true;
        return acc;
    }, {});
};
