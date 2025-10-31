import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';
import {
    COMPANY_ADDRESS_VERIFICATION_OPTIONS,
    DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from './Steps/BusinessStep/constants';

// Step 1: Eligibility validation.
export const eligibilityStepSchema = Yup.object().shape({
    relationship: Yup.string().required(
        'Please select your relationship to this production location',
    ),
});

// Step 2: Contact validation.
export const contactStepSchema = Yup.object().shape({
    contactEmail: Yup.string()
        .email('Invalid email address')
        .required('Contact email is required'),
    contactPhone: Yup.string(),
});

// Step 3: Business validation.
const getVerificationLabel = value =>
    COMPANY_ADDRESS_VERIFICATION_OPTIONS.find(opt => opt.value === value)
        ?.label;

const companyLinkedinAddressLabel = getVerificationLabel('linkedin-address');
const companyWebsiteAddressLabel = getVerificationLabel(
    'company-website-address',
);

const companyDocumentBasedLabels = DOCUMENT_BASED_VERIFICATION_OPTIONS.map(
    getVerificationLabel,
);

const getCompanyUrlValidationSchema = label =>
    Yup.string().when('locationAddressVerificationMethod', {
        is: value => value === label,
        then: schema =>
            schema
                .url('Invalid URL format')
                .required(
                    'The company address verification URL is required when this address verification method is selected',
                ),
    });

export const businessStepSchema = Yup.object().shape({
    locationAddressVerificationMethod: Yup.string().required(
        'Company address verification method is required',
    ),
    businessLinkedinProfile: getCompanyUrlValidationSchema(
        companyLinkedinAddressLabel,
    ),
    businessWebsite: getCompanyUrlValidationSchema(companyWebsiteAddressLabel),
    companyAddressVerificationDocuments: Yup.array().when(
        'locationAddressVerificationMethod',
        {
            is: value => companyDocumentBasedLabels.includes(value),
            then: schema =>
                schema
                    .min(1, 'At least one verification document is required')
                    .required('Verification documents are required'),
        },
    ),
});

// Step 4: Profile validation.
export const profileStepSchema = Yup.object().shape({
    // Production Location Overview
    localLanguageName: Yup.string().trim(),
    officePhoneNumber: Yup.string().trim(),
    businessWebsite: Yup.string().url('Invalid URL'),
    facilityDescription: Yup.string().trim(),

    // Company Information
    parentCompanyName: Yup.string(),
    officeOfficialName: Yup.string().trim(),
    officeAddress: Yup.string().trim(),
    officeCountryCode: Yup.string(),

    // Operations & Capabilities
    sectors: Yup.array(),
    facilityType: Yup.array(),
    facilityProductionTypes: Yup.array(),
    facilityProductTypes: Yup.array(),
    numberOfWorkers: Yup.string()
        .nullable()
        .test(
            'is-valid-workers',
            'Must be a positive integer or an ascending range (e.g., 100-500)',
            value => {
                if (!value || value.trim() === '') return true;

                const trimmedValue = value.trim();

                const hyphenIndex = trimmedValue.indexOf('-');
                if (hyphenIndex > 0) {
                    const parts = trimmedValue
                        .split('-')
                        .map(part => part.trim())
                        .filter(part => part !== '');

                    if (parts.length !== 2) return false;

                    const min = parseInt(parts[0], 10);
                    const max = parseInt(parts[1], 10);

                    if (
                        Number.isNaN(min) ||
                        Number.isNaN(max) ||
                        min < 1 ||
                        max < 1
                    ) {
                        return false;
                    }

                    if (parts[0] !== String(min) || parts[1] !== String(max)) {
                        return false;
                    }

                    return min < max;
                }

                const num = parseInt(trimmedValue, 10);

                if (
                    Number.isNaN(num) ||
                    num < 1 ||
                    trimmedValue !== String(num)
                ) {
                    return false;
                }

                return true;
            },
        ),
    facilityFemaleWorkersPercentage: Yup.string()
        .nullable()
        .test('is-valid-percentage', 'Must be between 0 and 100', value => {
            if (!value || value.trim() === '') return true;

            const cleanValue = value.replace('%', '').trim();
            const num = Number(cleanValue);
            return !Number.isNaN(num) && num >= 0 && num <= 100;
        }),
    facilityMinimumOrderQuantity: Yup.string().trim(),
    facilityAverageLeadTime: Yup.string().trim(),

    // Compliance & Partnerships
    facilityAffiliations: Yup.array(),
    facilityCertifications: Yup.array(),
});

export const getValidationSchemaForStep = stepIndex => {
    const schemas = {
        [CLAIM_FORM_STEPS.ELIGIBILITY]: eligibilityStepSchema,
        [CLAIM_FORM_STEPS.CONTACT]: contactStepSchema,
        [CLAIM_FORM_STEPS.BUSINESS]: businessStepSchema,
        [CLAIM_FORM_STEPS.PROFILE]: profileStepSchema,
    };

    return schemas[stepIndex] || Yup.object().shape({});
};
