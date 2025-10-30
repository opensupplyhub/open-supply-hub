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
    businessName: Yup.string().required('Business name is required'),
    businessWebsite: Yup.string().url('Invalid URL'),
});

// Step 4: Profile validation.
export const profileStepSchema = Yup.object().shape({
    // Production Location Overview
    localLanguageName: Yup.string(),
    officePhoneNumber: Yup.string(),
    businessWebsite: Yup.string().url('Invalid URL'),
    facilityDescription: Yup.string(),

    // Company Information
    parentCompanyName: Yup.string(),
    officeOfficialName: Yup.string(),
    officeAddress: Yup.string(),
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
    facilityMinimumOrderQuantity: Yup.string(),
    facilityAverageLeadTime: Yup.string(),

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
