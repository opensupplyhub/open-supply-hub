import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';

// Step 1: Eligibility validation.
export const eligibilityStepSchema = Yup.object().shape({
    position: Yup.string().required('Position/Title is required'),
    yearsAtCompany: Yup.string(),
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
    businessName: Yup.string().required('Business name is required'),
    businessWebsite: Yup.string().url('Invalid URL'),
});

// Step 4: Profile validation.
export const profileStepSchema = Yup.object().shape({
    // Production Location Overview
    localLanguageName: Yup.string(),
    facilityPhone: Yup.string(),
    facilityWebsite: Yup.string()
        .nullable()
        .test('is-valid-url', 'Must be a valid URL', value => {
            if (!value || value.trim() === '') return true; // Optional.
            try {
                const url = new URL(value);
                return !!url;
            } catch {
                return false;
            }
        }),
    description: Yup.string(),

    // Company Information
    parentCompanyName: Yup.mixed().nullable(),
    officeName: Yup.string(),
    officeAddress: Yup.string(),
    officeCountry: Yup.mixed().nullable(),

    // Operations & Capabilities
    sector: Yup.array(),
    locationType: Yup.array(),
    processingType: Yup.array(),
    productTypes: Yup.array(),
    numberOfWorkers: Yup.string()
        .nullable()
        .test('is-valid-workers', 'Must be a positive integer', value => {
            if (!value || value.trim() === '') return true; // Optional.

            const num = Number(value);
            return !Number.isNaN(num) && num >= 1 && Number.isInteger(num);
        }),
    femaleWorkers: Yup.string()
        .nullable()
        .test('is-valid-percentage', 'Must be between 0 and 100', value => {
            if (!value || value.trim() === '') return true; // Optional.

            // Remove % sign if present
            const cleanValue = value.replace('%', '').trim();
            const num = Number(cleanValue);
            return !Number.isNaN(num) && num >= 0 && num <= 100;
        }),
    minimumOrderQuantity: Yup.string(),
    averageLeadTime: Yup.string(),

    // Compliance & Partnerships
    affiliations: Yup.array(),
    certifications: Yup.array(),
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
