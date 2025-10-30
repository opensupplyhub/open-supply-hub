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
const getEmploymentVerificationLabel = value =>
    EMPLOYMENT_VERIFICATION_OPTIONS.find(opt => opt.value === value)?.label;

const urlEmploymentVerificationBasedLabels = URL_BASED_VERIFICATION_OPTIONS.map(
    getEmploymentVerificationLabel,
);

const documentEmploymentVerificationBasedLabels = DOCUMENT_BASED_VERIFICATION_OPTIONS.map(
    getEmploymentVerificationLabel,
);

export const contactStepSchema = Yup.object().shape({
    // Always required (claimant fields).
    claimantName: Yup.string()
        .trim()
        .required('Your full name is required field!'),
    claimantTitle: Yup.string()
        .trim()
        .required('Your job title is required field!'),

    // Toggle controlling public contact block visibility.
    publicContactEnabled: Yup.boolean().nullable(),

    contactPhone: Yup.string(),

    // Required only if public contact block is visible.
    contactName: Yup.string().when('publicContactEnabled', {
        is: v => v === true,
        then: s => s.trim().required('Contact name is required field!'), // NOSONAR
        otherwise: s => s.strip().nullable(),
    }),
    contactEmail: Yup.string()
        .email('Invalid email address')
        .when('publicContactEnabled', {
            is: v => v === true,
            then: s => s.required('Contact email is required field!'), // NOSONAR
            otherwise: s => s.strip().nullable(),
        }),
    employmentVerification: Yup.string().required(
        'Please select an employment verification option',
    ),
    employmentVerificationUrl: Yup.string().when('employmentVerification', {
        is: value => urlEmploymentVerificationBasedLabels.includes(value),
        then: (
            schema, // NOSONAR
        ) =>
            schema
                .url('Invalid URL format')
                .required(
                    'Employment verification URL is required on this employment verification method',
                ),
    }),
    employmentVerificationDocuments: Yup.array().when(
        'employmentVerification',
        {
            is: value =>
                documentEmploymentVerificationBasedLabels.includes(value),
            then: (
                schema, // NOSONAR
            ) =>
                schema
                    .min(1, 'At least one verification document is required')
                    .required('Verification documents are required'),
        },
    ),
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

// Step 4: Profile validation (all optional fields).
export const profileStepSchema = Yup.object().shape({
    numberOfWorkers: Yup.string()
        .nullable()
        .test('is-valid-workers', 'Must be at least 1 worker', value => {
            if (!value || value.trim() === '') return true; // Optional.

            const num = Number(value);
            return !Number.isNaN(num) && num >= 1 && Number.isInteger(num);
        }),
    additionalNotes: Yup.string(),
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
