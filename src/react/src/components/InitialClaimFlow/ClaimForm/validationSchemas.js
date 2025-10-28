import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';

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
export const businessStepSchema = Yup.object().shape({
    companyAddressVerification: Yup.string().required(
        'Company address verification method is required',
    ),
    verificationUrl: Yup.string()
        .when('companyAddressVerification', (val, schema) => {
            if (
                val === 'company-website-address' ||
                val === 'linkedin-address'
            ) {
                return schema
                    .url('Invalid URL format')
                    .required('Verification URL is required');
            }
            return schema.nullable();
        })
        .required('Verification URL is required'),
    verificationDocuments: Yup.array()
        .when('companyAddressVerification', (val, schema) => {
            if (
                val === 'utility-bill' ||
                val === 'business-registration' ||
                val === 'tax-license' ||
                val === 'property-lease' ||
                val === 'official-documents'
            ) {
                return schema
                    .min(1, 'At least one verification document is required')
                    .required('Verification documents are required');
            }
            return schema.nullable();
        })
        .required('Verification documents are required'),
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
