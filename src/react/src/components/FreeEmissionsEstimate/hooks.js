import { useFormik } from 'formik';
import { useEffect } from 'react';
import { freeEmissionsEstimateValidationSchema } from './utils.js';

// Custom hook to sync form field with Redux store.
export const useFormFieldSync = (formValue, storeValue, updateAction) => {
    useEffect(() => {
        if (formValue !== storeValue) {
            updateAction(formValue);
        }
    }, [formValue, storeValue, updateAction]);
};

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
