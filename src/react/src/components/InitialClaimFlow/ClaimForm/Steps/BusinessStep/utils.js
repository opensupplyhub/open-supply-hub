import {
    URL_BASED_VERIFICATION_OPTIONS,
    DOCUMENT_BASED_VERIFICATION_OPTIONS,
    COMPANY_ADDRESS_VERIFICATION_OPTIONS,
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
        case COMPANY_ADDRESS_VERIFICATION_OPTIONS.find(
            option => option.value === 'linkedin-address',
        )?.label:
            return 'https://linkedin.com/company/yourcompany';
        case COMPANY_ADDRESS_VERIFICATION_OPTIONS.find(
            option => option.value === 'company-website-address',
        )?.label:
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
        case COMPANY_ADDRESS_VERIFICATION_OPTIONS.find(
            option => option.value === 'linkedin-address',
        )?.label:
            return 'Company LinkedIn Page URL';
        case COMPANY_ADDRESS_VERIFICATION_OPTIONS.find(
            option => option.value === 'company-website-address',
        )?.label:
            return 'Company Website URL';
        default:
            return 'Website URL';
    }
};
