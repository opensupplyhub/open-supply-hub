import { useEffect } from 'react';

/**
 * Hook to reset the form to the first step on component mount
 * This ensures that direct URL access or page reload always starts at step 0
 * @param {Function} setActiveStep - Redux action to set the active step
 */
export const useStepResetOnMount = setActiveStep => {
    useEffect(() => {
        setActiveStep(0);
    }, [setActiveStep]);
};

/**
 * Hook to prefetch data when component mounts
 * @param {Function} fetchData - Function to dispatch data fetching
 * @param {string} osID - The facility OS ID
 */
export const usePrefetchData = (fetchData, osID) => {
    useEffect(() => {
        if (osID) {
            fetchData(osID);
        }
    }, [fetchData, osID]);
};

/**
 * Hook to validate current step before allowing navigation
 * @param {Object} formValues - Current form values
 * @param {Function} validateForm - Formik's validateForm function
 * @returns {Function} - Validation function that returns a promise
 */
export const useStepValidation = (formValues, validateForm) => {
    const validateCurrentStep = async () => {
        const errors = await validateForm(formValues);
        return Object.keys(errors).length === 0;
    };

    return validateCurrentStep;
};
