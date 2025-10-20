import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';

// Step 1: Eligibility validation
export const eligibilityStepSchema = Yup.object().shape({
    eligibilityConfirmed: Yup.boolean()
        .oneOf([true], 'You must confirm eligibility')
        .required('Required'),
});

// Step 2: Contact validation (basic structure for now)
export const contactStepSchema = Yup.object().shape({
    claimantName: Yup.string(),
    claimantTitle: Yup.string(),
    claimantEmail: Yup.string().email('Invalid email address'),
    verificationMethod: Yup.string(),
});

// Step 3: Business validation (basic structure for now)
export const businessStepSchema = Yup.object().shape({
    businessWebsite: Yup.string().url('Invalid URL'),
    companyAddressVerification: Yup.string(),
});

// Step 4: Profile validation (optional fields)
export const profileStepSchema = Yup.object().shape({
    facilityName: Yup.string(),
    sector: Yup.array(),
    facilityPhone: Yup.string(),
    facilityWebsite: Yup.string().url('Invalid URL'),
    localLanguageName: Yup.string(),
    numberOfWorkers: Yup.string(),
    femaleWorkers: Yup.string(),
    minimumOrderQuantity: Yup.string(),
    averageLeadTime: Yup.string(),
    facilityTypes: Yup.array(),
    productTypes: Yup.string(),
    parentCompanyName: Yup.string(),
    officeName: Yup.string(),
    officeAddress: Yup.string(),
    officeCountry: Yup.string(),
    affiliations: Yup.array(),
    certifications: Yup.array(),
    description: Yup.string(),
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
