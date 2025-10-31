import { CLAIM_FORM_STEPS, TOTAL_STEPS } from './constants';

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
