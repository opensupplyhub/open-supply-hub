import { useEffect } from 'react';
import { useFormik } from 'formik';
import { getValidationSchemaForStep } from './validationSchemas';

export const usePrefetchData = (fetchData, osID) => {
    useEffect(() => {
        if (osID) {
            fetchData(osID);
        }
    }, [fetchData, osID]);
};

export const useClaimForm = (
    initialValues,
    activeStep,
    updateField,
    onSubmit,
) => {
    const formik = useFormik({
        initialValues,
        validationSchema: getValidationSchemaForStep(activeStep),
        onSubmit,
    });

    // Re-validate when step changes to populate errors for new schema.
    useEffect(() => {
        const schema = getValidationSchemaForStep(activeStep);
        const currentStepFields = Object.keys(schema.describe().fields);

        // Mark fields with values as touched when returning to a step.
        const fieldsToTouch = {};
        currentStepFields.forEach(field => {
            if (formik.values[field] && formik.values[field] !== '') {
                fieldsToTouch[field] = true;
            }
        });

        if (Object.keys(fieldsToTouch).length > 0) {
            formik.setTouched(fieldsToTouch);
        }

        // Validate to populate errors for current step.
        formik.validateForm();
    }, [activeStep]);

    // Custom field change handler that syncs to Redux.
    const handleFieldChange = (field, value) => {
        formik.setFieldValue(field, value);
        formik.setFieldTouched(field, true, false);
        updateField({ field, value });
    };

    // Calculate button disabled state for current step.
    const getButtonDisabledState = () => {
        const schema = getValidationSchemaForStep(activeStep);
        const currentStepFields = Object.keys(schema.describe().fields);

        // Check if user has interacted with any field in current step.
        const hasInteractedWithCurrentStep = currentStepFields.some(
            field => formik.touched[field],
        );

        // Check if there are validation errors in CURRENT STEP ONLY.
        const hasCurrentStepErrors = currentStepFields.some(
            field => formik.errors[field],
        );

        // Only disable button if user has interacted AND there are errors.
        return hasInteractedWithCurrentStep && hasCurrentStepErrors;
    };

    return {
        claimForm: formik,
        handleFieldChange,
        isButtonDisabled: getButtonDisabledState(),
    };
};
