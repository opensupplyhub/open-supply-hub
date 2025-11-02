import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';
import {
    EMPLOYMENT_VERIFICATION_OPTIONS,
    EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from './Steps/ContactInfoStep/constants';
import {
    COMPANY_ADDRESS_VERIFICATION_OPTIONS,
    DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from './Steps/BusinessStep/constants';

// Step 1: Eligibility validation.
export const eligibilityStepSchema = Yup.object().shape({
    claimantLocationRelationship: Yup.string().required(
        'Please select your relationship to this production location',
    ),
});

// Step 2: Contact validation.
const getEmploymentVerificationLabel = value =>
    EMPLOYMENT_VERIFICATION_OPTIONS.find(opt => opt.value === value)?.label;

const documentEmploymentVerificationBasedLabels = new Set(
    EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS.map(
        getEmploymentVerificationLabel,
    ),
);

const getClaimantUrlValidationSchema = label =>
    Yup.string().when('claimantEmploymentVerificationMethod', {
        is: value => value === label,
        then: schema =>
            schema
                .url('Invalid URL format')
                .required(
                    'Employment verification URL is required on this employment verification method',
                ),
    });

export const contactStepSchema = Yup.object().shape({
    // Always required (claimant fields).
    yourName: Yup.string().trim().required('Your full name is required field!'),
    yourTitle: Yup.string()
        .trim()
        .required('Your job title is required field!'),

    claimantEmploymentVerificationMethod: Yup.string().required(
        'Please select an employment verification option',
    ),

    // Company LinkedIn URL required if company LinkedIn page option is selected
    claimantLinkedinProfileUrl: getClaimantUrlValidationSchema(
        getEmploymentVerificationLabel('linkedin-page'),
    ),
    // Company website URL required if website option is selected
    yourBusinessWebsite: getClaimantUrlValidationSchema(
        getEmploymentVerificationLabel('company-website-address'),
    ),

    employmentVerificationDocuments: Yup.array().when(
        'claimantEmploymentVerificationMethod',
        {
            is: label => documentEmploymentVerificationBasedLabels.has(label),
            then: schema =>
                schema
                    .min(1, 'At least one verification document is required')
                    .required('Verification documents are required'),
        },
    ),

    // Toggle controlling public contact block visibility.
    pointOfContactPubliclyVisible: Yup.boolean().nullable(),

    // Required only if public contact block is visible.
    pointOfcontactPersonName: Yup.string().when(
        'pointOfContactPubliclyVisible',
        {
            is: v => v === true,
            then: s => s.trim().required('Contact name is required field!'),
            otherwise: s => s.strip().nullable(),
        },
    ),
    pointOfContactEmail: Yup.string()
        .email('Invalid email address')
        .when('pointOfContactPubliclyVisible', {
            is: v => v === true,
            then: s => s.required('Contact email is required field!'),
            otherwise: s => s.strip().nullable(),
        }),
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
                .required('The company address verification URL is required'),
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
