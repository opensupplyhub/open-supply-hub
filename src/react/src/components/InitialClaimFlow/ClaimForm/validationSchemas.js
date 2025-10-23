import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';

// Step 1: Eligibility validation
export const eligibilityStepSchema = Yup.object().shape({
    position: Yup.string().required('Position/Title is required'),
    yearsAtCompany: Yup.string(),
});

// Step 2: Contact validation
export const contactStepSchema = Yup.object().shape({
    contactEmail: Yup.string()
        .email('Invalid email address')
        .required('Contact email is required'),
    contactPhone: Yup.string(),
});

// Step 3: Business validation
export const businessStepSchema = Yup.object().shape({
    businessName: Yup.string().required('Business name is required'),
    businessWebsite: Yup.string().url('Invalid URL'),
});

// Step 4: Profile validation (all optional fields)
export const profileStepSchema = Yup.object().shape({
    numberOfWorkers: Yup.string()
        .nullable()
        .test('is-valid-workers', 'Must be at least 1 worker', value => {
            if (!value || value.trim() === '') return true; // Optional

            const num = Number(value);
            return !Number.isNaN(num) && num >= 1 && Number.isInteger(num);
        }),
    additionalNotes: Yup.string(),
});

/**
 * Get the appropriate validation schema for a given step
 * @param {number} stepIndex - The index of the step
 * @returns {Yup.ObjectSchema} - The validation schema for the step
 */
export const getValidationSchemaForStep = stepIndex => {
    const schemas = {
        [CLAIM_FORM_STEPS.ELIGIBILITY]: eligibilityStepSchema,
        [CLAIM_FORM_STEPS.CONTACT]: contactStepSchema,
        [CLAIM_FORM_STEPS.BUSINESS]: businessStepSchema,
        [CLAIM_FORM_STEPS.PROFILE]: profileStepSchema,
    };

    return schemas[stepIndex] || Yup.object().shape({});
};
