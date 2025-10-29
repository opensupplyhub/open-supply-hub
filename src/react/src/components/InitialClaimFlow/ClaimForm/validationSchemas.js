import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';
import {
    COMPANY_ADDRESS_VERIFICATION_OPTIONS,
    URL_BASED_VERIFICATION_OPTIONS,
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

const urlBasedLabels = URL_BASED_VERIFICATION_OPTIONS.map(getVerificationLabel);

const documentBasedLabels = DOCUMENT_BASED_VERIFICATION_OPTIONS.map(
    getVerificationLabel,
);

export const businessStepSchema = Yup.object().shape({
    companyAddressVerification: Yup.string().required(
        'Company address verification method is required',
    ),
    companyAddressVerificationUrl: Yup.string().when(
        'companyAddressVerification',
        {
            is: value => urlBasedLabels.includes(value),
            then: schema =>
                schema
                    .url('Invalid URL format')
                    .required(
                        'Company address verification URL is required on this address verification method',
                    ),
        },
    ),
    companyAddressVerificationDocuments: Yup.array().when(
        'companyAddressVerification',
        {
            is: value => documentBasedLabels.includes(value),
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
