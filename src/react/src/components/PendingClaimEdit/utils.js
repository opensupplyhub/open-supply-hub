import camelCase from 'lodash/camelCase';
import snakeCase from 'lodash/snakeCase';

import {
    extractSelectValue,
    filterFreeEmissionsEstimateFields,
} from '../../util/util';

/*
 * The single place the API <-> form field mapping lives for the
 * pending-claim edit view (OSDEV-3371).
 *
 * The pending-claim API payload uses the claim form's snake_case field
 * names (the same names FacilityCreateClaimSerializer accepts), and the
 * claim form's Redux/Formik state uses their camelCase equivalents —
 * the identical convention the create flow relies on when it
 * snake-cases keys at submit time (actions/claimForm.js).
 */

// Fields that hold File objects picked in the UI; they are uploaded to
// the attachments sub-resource, never sent in the PATCH payload.
export const DOCUMENT_FIELDS = [
    'employmentVerificationDocuments',
    'companyAddressVerificationDocuments',
];

// Client-only fields that must never reach the API.
const CLIENT_ONLY_FIELDS = new Set([
    ...DOCUMENT_FIELDS,
    'attachments',
    'id',
    'status',
    'createdAt',
    'updatedAt',
    'claimantUpdatedAt',
    'osId',
    'facilityName',
]);

// Numeric/date fields where an empty string means "not provided" and
// must be omitted rather than sent (the API rejects '' for them).
const OMIT_WHEN_EMPTY_FIELDS = new Set([
    'openingDate',
    'estimatedAnnualThroughput',
    'facilityFemaleWorkersPercentage',
    'numberOfWorkers',
    'energyCoal',
    'energyNaturalGas',
    'energyDiesel',
    'energyKerosene',
    'energyBiomass',
    'energyCharcoal',
    'energyAnimalWaste',
    'energyElectricity',
    'energyOther',
]);

// Multi-select fields: the API stores/accepts plain string arrays, but
// the form's StyledSelect components work with {value, label} option
// objects — the same shape the create flow keeps in Redux and unwraps
// via extractSelectValue at submit time (appendArrayField).
const SELECT_OPTION_ARRAY_FIELDS = [
    'sectors',
    'facilityType',
    'facilityProductTypes',
    'facilityProductionTypes',
    'facilityAffiliations',
    'facilityCertifications',
];

const ENERGY_VALUE_TO_ENABLED = Object.freeze({
    energyCoal: 'energyCoalEnabled',
    energyNaturalGas: 'energyNaturalGasEnabled',
    energyDiesel: 'energyDieselEnabled',
    energyKerosene: 'energyKeroseneEnabled',
    energyBiomass: 'energyBiomassEnabled',
    energyCharcoal: 'energyCharcoalEnabled',
    energyAnimalWaste: 'energyAnimalWasteEnabled',
    energyElectricity: 'energyElectricityEnabled',
    energyOther: 'energyOtherEnabled',
});

// The claim form keeps numeric inputs as strings ('' when blank); the
// API returns numbers. Coerce for display so controlled inputs behave.
const NUMERIC_STRING_FIELDS = new Set([
    'estimatedAnnualThroughput',
    'facilityFemaleWorkersPercentage',
    ...Object.keys(ENERGY_VALUE_TO_ENABLED),
]);

const toSelectOptions = values =>
    (Array.isArray(values) ? values : []).map(value => ({
        value,
        label: value,
    }));

/*
 * Map a GET /pending/ payload onto the claim form's camelCase formData
 * shape, so the create flow's step components render it unchanged.
 */
export const pendingClaimApiToFormData = apiData => {
    const formData = {};

    Object.entries(apiData || {}).forEach(([key, value]) => {
        const formKey = camelCase(key);
        if (formKey === 'attachments') {
            return;
        }
        formData[formKey] = value === null ? '' : value;
    });

    // facility_type is stored pipe-joined; the form works with an array.
    if (typeof formData.facilityType === 'string') {
        formData.facilityType = formData.facilityType
            ? formData.facilityType.split('|')
            : [];
    }

    // Wrap multi-select values as {value, label} options — the shape
    // the form's select components render. Plain strings display as
    // empty chips.
    SELECT_OPTION_ARRAY_FIELDS.forEach(field => {
        formData[field] = toSelectOptions(formData[field]);
    });

    // Numeric inputs are controlled text fields holding strings.
    NUMERIC_STRING_FIELDS.forEach(field => {
        if (formData[field] !== '' && formData[field] !== undefined) {
            formData[field] = String(formData[field]);
        }
    });

    // Derive the emissions-section checkbox state from stored values.
    Object.entries(ENERGY_VALUE_TO_ENABLED).forEach(
        ([valueField, enabledField]) => {
            formData[enabledField] =
                formData[valueField] !== '' &&
                formData[valueField] !== undefined;
        },
    );

    // Document pickers always start empty; existing uploads are shown
    // in the attachments section instead.
    DOCUMENT_FIELDS.forEach(field => {
        formData[field] = [];
    });

    return formData;
};

/*
 * Build the JSON PATCH payload from formData: strip client-only fields,
 * drop disabled emissions fields (same behavior as the create flow's
 * filterFreeEmissionsEstimateFields), omit empty numeric/date fields,
 * unwrap select option objects to plain strings (extractSelectValue,
 * exactly like the create flow's appendArrayField), pipe-join
 * facilityType, and snake_case every key.
 */
export const buildPendingClaimPatchPayload = formData => {
    const filtered = filterFreeEmissionsEstimateFields(formData);
    const payload = {};

    Object.entries(filtered).forEach(([key, value]) => {
        if (CLIENT_ONLY_FIELDS.has(key) || key.endsWith('Enabled')) {
            return;
        }
        if (
            OMIT_WHEN_EMPTY_FIELDS.has(key) &&
            (value === '' || value === null || value === undefined)
        ) {
            return;
        }
        if (value === undefined) {
            return;
        }

        let outValue = value;
        if (key === 'facilityType') {
            if (!Array.isArray(value) || value.length === 0) {
                return;
            }
            outValue = value.map(extractSelectValue).join('|');
        } else if (SELECT_OPTION_ARRAY_FIELDS.includes(key)) {
            outValue = (Array.isArray(value) ? value : []).map(
                extractSelectValue,
            );
        }

        payload[snakeCase(key)] = outValue;
    });

    return payload;
};
