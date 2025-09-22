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

// Free Emissions Estimate Formik validation schema
export const freeEmissionsEstimateValidationSchema = objectYup({
    openingDate: stringYup(),
    closingDate: stringYup(),
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
