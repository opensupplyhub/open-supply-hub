import { string as stringYup, object as objectYup } from 'yup';

const parseDate = dateString => {
    if (!dateString) return null;

    // Create Date object from ISO string (YYYY-MM-DD).
    const date = new Date(dateString);

    // Check if the date is valid.
    return Number.isNaN(date.getTime()) ? null : date;
};

const baseDateValidation = stringYup().test(
    'valid-date-not-future',
    'Please enter a valid date (not in the future).',
    value => {
        if (!value) return true;
        const date = parseDate(value);
        if (!date) return false;
        return date <= new Date();
    },
);

const createDateComparisonValidator = (otherFieldName, comparisonFn) =>
    function (value) {
        const otherValue = this.parent[otherFieldName];

        // If either date is empty, skip validation.
        if (!value || !otherValue) {
            return true;
        }

        const currentDate = parseDate(value);
        const otherDate = parseDate(otherValue);

        return comparisonFn(currentDate, otherDate);
    };

const isValidPositiveInteger = value => {
    const numericValue = parseInt(value, 10);
    return (
        !Number.isNaN(numericValue) &&
        numericValue > 0 &&
        value === numericValue.toString()
    );
};

const createPositiveIntegerValidation = schema =>
    schema
        .test(
            'is-trimmed',
            'Remove spaces at start and end of the provided value.',
            value => value == null || value === value.trim(),
        )
        .test(
            'valid-positive-integer',
            'Please enter a positive integer.',
            value => !value || isValidPositiveInteger(value),
        );

const createEnergyFieldValidation = enabledField =>
    stringYup().when(enabledField, {
        is: true,
        then: schema => createPositiveIntegerValidation(schema),
    });

// Free missions estimate Yup validation schema.
const freeEmissionsEstimateValidationSchema = objectYup({
    openingDate: baseDateValidation.test(
        'opening-before-closing',
        'Opening date must be before or equal to closing date.',
        createDateComparisonValidator(
            'closingDate',
            (opening, closing) => opening <= closing,
        ),
    ),
    closingDate: baseDateValidation.test(
        'closing-after-opening',
        'Closing date must be after or equal to opening date.',
        createDateComparisonValidator(
            'openingDate',
            (closing, opening) => closing >= opening,
        ),
    ),
    estimatedAnnualThroughput: createPositiveIntegerValidation(stringYup()),
    energyCoal: createEnergyFieldValidation('energyCoalEnabled'),
    energyNaturalGas: createEnergyFieldValidation('energyNaturalGasEnabled'),
    energyDiesel: createEnergyFieldValidation('energyDieselEnabled'),
    energyKerosene: createEnergyFieldValidation('energyKeroseneEnabled'),
    energyBiomass: createEnergyFieldValidation('energyBiomassEnabled'),
    energyCharcoal: createEnergyFieldValidation('energyCharcoalEnabled'),
    energyAnimalWaste: createEnergyFieldValidation('energyAnimalWasteEnabled'),
    energyElectricity: createEnergyFieldValidation('energyElectricityEnabled'),
    energyOther: createEnergyFieldValidation('energyOtherEnabled'),
});

export default freeEmissionsEstimateValidationSchema;
