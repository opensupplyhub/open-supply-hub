import { useEffect } from 'react';

/**
 * Custom hook to handle verification URL field clearing when verification method changes.
 * Clears the URL field when switching between different verification methods.
 */
const useVerificationMethodChange = (
    verificationMethod,
    prevVerificationMethod,
    handleFieldChange,
) => {
    useEffect(() => {
        if (
            verificationMethod !== prevVerificationMethod &&
            prevVerificationMethod
        ) {
            // Clear verification URL when switching methods.
            handleFieldChange('verificationUrl', '');
        }
    }, [verificationMethod, prevVerificationMethod, handleFieldChange]);
};

export default useVerificationMethodChange;
