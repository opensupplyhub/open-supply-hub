import { useEffect } from 'react';

/**
 * Custom hook to handle verification URL field clearing when verification
 * method changes. Clears the URL and documents fields when switching
 * between different verification methods.
 */
const useVerificationMethodChange = (
    verificationMethod,
    prevVerificationMethod,
    updateField,
) => {
    useEffect(() => {
        if (
            prevVerificationMethod &&
            verificationMethod !== prevVerificationMethod
        ) {
            // Clear verification URL and documents when switching methods.
            updateField('employmentVerificationUrl', '');
            updateField('employmentVerificationDocuments', []);
        }
    }, [verificationMethod, prevVerificationMethod, updateField]);
};

export default useVerificationMethodChange;
