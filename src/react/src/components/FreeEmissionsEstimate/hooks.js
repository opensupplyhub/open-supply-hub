import { useFormik } from 'formik';
import { freeEmissionsEstimateValidationSchema } from './utils.js';

export const useFreeEmissionsEstimateForm = (initialValues, onSubmit) =>
    useFormik({
        initialValues: {
            openingDate: '',
            closingDate: '',
            annualThroughput: '',
            energyCoal: '',
            energyNaturalGas: '',
            energyDiesel: '',
            energyKerosene: '',
            energyBiomass: '',
            energyCharcoal: '',
            energyAnimalWaste: '',
            energyElectricity: '',
            energyOther: '',
            energyCoalEnabled: false,
            energyNaturalGasEnabled: false,
            energyDieselEnabled: false,
            energyKeroseneEnabled: false,
            energyBiomassEnabled: false,
            energyCharcoalEnabled: false,
            energyAnimalWasteEnabled: false,
            energyElectricityEnabled: false,
            energyOtherEnabled: false,
            ...initialValues,
        },
        validationSchema: freeEmissionsEstimateValidationSchema,
        onSubmit: onSubmit || (() => {}),
        validateOnMount: false,
        enableReinitialize: true,
    });
