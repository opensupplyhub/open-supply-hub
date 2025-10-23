import { useEffect } from 'react';

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
