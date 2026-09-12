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

const WEBSITE_MAX_LENGTH = 200;

const getClaimantUrlValidationSchema = label =>
    Yup.string().when('claimantEmploymentVerificationMethod', {
        is: value => value === label,
        then: schema =>
            schema
                .url('Invalid URL format. Example: https://company.com')
                .max(
                    WEBSITE_MAX_LENGTH,
                    `URL must be ${WEBSITE_MAX_LENGTH} characters or fewer`,
                )
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
    pointOfContactPersonName: Yup.string().when(
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
                .url('Invalid URL format. Example: https://company.com')
                .max(
                    WEBSITE_MAX_LENGTH,
                    `URL must be ${WEBSITE_MAX_LENGTH} characters or fewer`,
                )
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

const SELECT_OPTION_MAX_LENGTH = 50;
const FACILITY_TYPE_JOINED_MAX_LENGTH = 300;
const TEXT_FIELD_MAX_LENGTH = 200;
const DESCRIPTION_MAX_LENGTH = 1000;

const maxLengthTextField = (fieldLabel, baseSchema = Yup.string()) =>
    baseSchema.max(
        TEXT_FIELD_MAX_LENGTH,
        `${fieldLabel} must be ${TEXT_FIELD_MAX_LENGTH} characters or fewer`,
    );

const extractSelectOptionText = value => {
    if (typeof value === 'object' && value !== null) {
        return value.value || value.label || '';
    }

    return String(value);
};

const selectOptionsMaxLengthSchema = fieldLabel =>
    Yup.array().test(
        'max-option-length',
        `Each ${fieldLabel} must be ${SELECT_OPTION_MAX_LENGTH} characters or fewer. Enter values separately using Enter or Tab.`,
        options => {
            if (!options?.length) {
                return true;
            }

            return options.every(
                value =>
                    String(extractSelectOptionText(value)).length <=
                    SELECT_OPTION_MAX_LENGTH,
            );
        },
    );

// Matches BE CharField(max_length=300) on the pipe-joined facility_type string.
const facilityTypeJoinedMaxLengthSchema = Yup.array().test(
    'max-joined-length',
    `Location types combined must be ${FACILITY_TYPE_JOINED_MAX_LENGTH} characters or fewer. Enter values separately using Enter or Tab.`,
    options => {
        if (!options?.length) {
            return true;
        }

        const joined = options.map(extractSelectOptionText).join('|');
        return joined.length <= FACILITY_TYPE_JOINED_MAX_LENGTH;
    },
);

// Step 4: Profile validation.
export const profileStepSchema = Yup.object().shape({
    // Production Location Overview
    localLanguageName: Yup.string().trim(),
    facilityPhoneNumber: maxLengthTextField(
        'Company phone',
        Yup.string().trim(),
    ),
    businessWebsite: Yup.string()
        .url('Invalid URL. Example: https://company.com')
        .max(
            WEBSITE_MAX_LENGTH,
            `Website URL must be ${WEBSITE_MAX_LENGTH} characters or fewer`,
        ),
    facilityDescription: Yup.string()
        .trim()
        .max(
            DESCRIPTION_MAX_LENGTH,
            `Description must be ${DESCRIPTION_MAX_LENGTH} characters or fewer`,
        ),

    // Company Information
    parentCompanyName: maxLengthTextField('Parent company name'),
    officeOfficialName: maxLengthTextField('Office name', Yup.string().trim()),
    officeAddress: maxLengthTextField('Office address', Yup.string().trim()),
    officeCountryCode: Yup.string(),

    // Operations & Capabilities
    sectors: selectOptionsMaxLengthSchema('sector'),
    facilityType: facilityTypeJoinedMaxLengthSchema,
    facilityProductionTypes: selectOptionsMaxLengthSchema('processing type'),
    facilityProductTypes: selectOptionsMaxLengthSchema('product type'),
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
    facilityMinimumOrderQuantity: maxLengthTextField(
        'Minimum order quantity',
        Yup.string().trim(),
    ),
    facilityAverageLeadTime: maxLengthTextField(
        'Average lead time',
        Yup.string().trim(),
    ),

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
