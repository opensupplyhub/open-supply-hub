import {
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
 */
export const buildProductionLocationUrl = osId => {
    if (!osId) return '#';
    const baseUrl = window.location.origin;
    return `${baseUrl}/facilities/${osId}`;
};
