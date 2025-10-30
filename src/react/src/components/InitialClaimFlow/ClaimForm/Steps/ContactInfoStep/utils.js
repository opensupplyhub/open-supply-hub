import {
    EMPLOYMENT_VERIFICATION_OPTIONS,
    URL_BASED_VERIFICATION_OPTIONS,
    DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from './constants';

/**
 * Determines if the verification method requires a URL input.
 */
export const requiresUrlInput = verificationMethod =>
    URL_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

/**
 * Determines if the verification method requires document upload.
 */
export const requiresDocumentUpload = verificationMethod =>
    DOCUMENT_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

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

/**
 * Gets the label text for URL input based on verification method.
 */
export const getUrlLabel = verificationMethod => {
    switch (verificationMethod) {
        case EMPLOYMENT_VERIFICATION_OPTIONS.find(
            option => option.value === 'linkedin-page',
        )?.label:
            return 'Your LinkedIn Page URL';
        case EMPLOYMENT_VERIFICATION_OPTIONS.find(
            option => option.value === 'company-website-address',
        )?.label:
            return 'Website URL';
        default:
            return 'Website URL';
    }
};
