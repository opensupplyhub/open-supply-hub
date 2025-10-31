import {
    EMPLOYMENT_VERIFICATION_OPTIONS,
    EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS,
    EMPLOYMENT_URL_BASED_VERIFICATION_OPTIONS,
} from './constants';

/**
 * Determines if the verification method requires a URL input.
 */
export const requiresUrlInput = verificationMethod =>
    EMPLOYMENT_URL_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

/**
 * Determines if the verification method requires document upload.
 */
export const requiresDocumentUpload = verificationMethod =>
    EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

/**
 * Gets the placeholder text for URL input based on verification method.
 */
export const getUrlPlaceholder = verificationMethod => {
    switch (verificationMethod) {
        case EMPLOYMENT_VERIFICATION_OPTIONS.find(
            option => option.value === 'linkedin-page',
        )?.label:
            return 'https://linkedin.com/in/yourprofile';
        case EMPLOYMENT_VERIFICATION_OPTIONS.find(
            option => option.value === 'company-website-address',
        )?.label:
            return 'https://company.com/about-us';
        default:
            return 'https://';
    }
};
