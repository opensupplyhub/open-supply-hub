import {
    URL_BASED_VERIFICATION_OPTIONS,
    DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from './constants';

export const requiresUrlInput = verificationMethod =>
    URL_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

export const requiresDocumentUpload = verificationMethod =>
    DOCUMENT_BASED_VERIFICATION_OPTIONS.includes(verificationMethod);

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

export const getVerificationUrlField = verificationMethod => {
    switch (verificationMethod) {
        case 'linkedin-address':
            return 'businessLinkedinProfile';
        case 'company-website-address':
            return 'businessWebsite';
        default:
            return '';
    }
};
