import {
    URL_BASED_VERIFICATION_OPTIONS,
    DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from './constants';

/**
 * Determines if the verification method requires a URL input.
 * @param {string} verificationMethod - The selected verification method value.
 * @returns {boolean} True if URL input is required, false otherwise.
 */
export const requiresUrlInput = verificationMethod =>
    URL_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

/**
 * Determines if the verification method requires document upload.
 * @param {string} verificationMethod - The selected verification method value.
 * @returns {boolean} True if document upload is required, false otherwise.
 */
export const requiresDocumentUpload = verificationMethod =>
    DOCUMENT_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

/**
 * Gets the placeholder text for URL input based on verification method.
 * @param {string} verificationMethod - The selected verification method value.
 * @returns {string} Placeholder text for URL input.
 */
export const getUrlPlaceholder = verificationMethod => {
    switch (verificationMethod) {
        case 'linkedin-address':
            return 'https://linkedin.com/company/yourcompany';
        case 'company-website-address':
            return 'https://company.com/contact-us';
        default:
            return 'https://';
    }
};

/**
 * Gets the label text for URL input based on verification method.
 * @param {string} verificationMethod - The selected verification method value.
 * @returns {string} Label text for URL input.
 */
export const getUrlLabel = verificationMethod => {
    switch (verificationMethod) {
        case 'linkedin-address':
            return 'Company LinkedIn Page URL';
        case 'company-website-address':
            return 'Company Website URL';
        default:
            return 'Website URL';
    }
};

/**
 * Builds the production location URL for the OS Hub platform.
 * @param {string} osId - The OS ID of the production location.
 * @returns {string} Full URL to the production location profile.
 */
export const buildProductionLocationUrl = osId => {
    if (!osId) return '#';
    const baseUrl = window.location.origin;
    return `${baseUrl}/facilities/${osId}`;
};
