import { string as stringYup, object as objectYup } from 'yup';
import { isEmpty } from 'lodash';

// Free Emissions Estimate validation utilities
export const isValidEnergyValue = value => {
    if (isEmpty(value)) {
        return true;
    }

    const numericValue = parseFloat(value);
    return !Number.isNaN(numericValue) && numericValue >= 0;
};

export const isValidAnnualThroughput = value => {
    if (isEmpty(value)) {
        return true;
    }

    // Allow formats like "10,000 kg/year", "5000 tons/month", etc.
    const cleanValue = value.replace(/[,\s]/g, '');
    const numericPart = cleanValue.match(/^\d+(\.\d+)?/);

    return numericPart !== null;
};

// Helper function to parse and compare dates
const parseDateForComparison = (dateString, isClosingDate = false) => {
    if (!dateString) return null;

    // Handle month/year format (e.g., "12/2024" or "1/2024")
    if (dateString.includes('/')) {
        const [month, year] = dateString
            .split('/')
            .map(part => parseInt(part, 10));
        return new Date(year, month - 1); // month is 0-indexed in Date constructor
    }

    // Handle year-only format (e.g., "2024")
    const year = parseInt(dateString, 10);
    if (Number.isNaN(year)) return null;

    // For opening date (year only), assume January 1st
    // For closing date (if year only), assume December 31st
    return new Date(year, isClosingDate ? 11 : 0, isClosingDate ? 31 : 1);
};

// Shared date comparison validation function
const createDateComparisonValidator = (otherFieldName, comparisonFn) =>
    function (value) {
        const otherValue = this.parent[otherFieldName];

        // If either date is empty, skip validation
        if (!value || !otherValue) {
            return true;
        }

        const currentFieldIsClosing = otherFieldName === 'openingDate';
        const currentDateParsed = parseDateForComparison(
            value,
            currentFieldIsClosing,
        );
        const otherDateParsed = parseDateForComparison(
            otherValue,
            !currentFieldIsClosing,
        );

        if (!currentDateParsed || !otherDateParsed) {
            return true; // Skip validation if parsing fails
        }

        return comparisonFn(currentDateParsed, otherDateParsed);
    };

// Free Emissions Estimate Formik validation schema
export const freeEmissionsEstimateValidationSchema = objectYup({
    openingDate: stringYup().test(
        'opening-before-closing',
        'Opening date must be before or equal to closing date.',
        createDateComparisonValidator(
            'closingDate',
            (opening, closing) => opening <= closing,
        ),
    ),
    closingDate: stringYup().test(
        'closing-after-opening',
        'Closing date must be after or equal to opening date.',
        createDateComparisonValidator(
            'openingDate',
            (closing, opening) => closing >= opening,
        ),
    ),
    annualThroughput: stringYup().test(
        'valid-throughput',
        'Please enter a valid throughput value (e.g., "10,000 kg/year").',
        value => !value || isValidAnnualThroughput(value),
    ),
    energyCoal: stringYup().when('energyCoalEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyNaturalGas: stringYup().when('energyNaturalGasEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyDiesel: stringYup().when('energyDieselEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyKerosene: stringYup().when('energyKeroseneEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyBiomass: stringYup().when('energyBiomassEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyCharcoal: stringYup().when('energyCharcoalEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyAnimalWaste: stringYup().when('energyAnimalWasteEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyElectricity: stringYup().when('energyElectricityEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
    energyOther: stringYup().when('energyOtherEnabled', {
        is: true,
        then: schema =>
            schema.test(
                'valid-energy',
                'Please enter a valid positive number.',
                value => !value || isValidEnergyValue(value),
            ),
    }),
});
