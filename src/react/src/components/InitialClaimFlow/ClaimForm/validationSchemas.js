import * as Yup from 'yup';
import { CLAIM_FORM_STEPS } from './constants';

// Step 1: Eligibility validation.
export const eligibilityStepSchema = Yup.object().shape({
    relationship: Yup.object().required(
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
    facilityPhone: Yup.string(),
    businessWebsite: Yup.string()
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
        .test(
            'is-valid-workers',
            'Must be a positive integer or an ascending range (e.g., 100-500)',
            value => {
                if (!value || value.trim() === '') return true; // Optional.

                const trimmedValue = value.trim();

                // Check if it's a range (contains hyphen not at the start)
                const hyphenIndex = trimmedValue.indexOf('-');
                if (hyphenIndex > 0) {
                    // Split by hyphen
                    const parts = trimmedValue
                        .split('-')
                        .map(part => part.trim())
                        .filter(part => part !== ''); // Remove empty strings

                    // Must have exactly 2 parts
                    if (parts.length !== 2) return false;

                    const min = parseInt(parts[0], 10);
                    const max = parseInt(parts[1], 10);

                    // Both must be valid positive integers
                    if (
                        Number.isNaN(min) ||
                        Number.isNaN(max) ||
                        min < 1 ||
                        max < 1
                    ) {
                        return false;
                    }

                    // Check if they're actually integers (no decimals)
                    if (parts[0] !== String(min) || parts[1] !== String(max)) {
                        return false;
                    }

                    // Min must be less than max (ascending range)
                    return min < max;
                }

                // Single number - must be positive integer
                const num = parseInt(trimmedValue, 10);

                // Check if it's a valid integer (no decimals, no leading zeros except for "0")
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
