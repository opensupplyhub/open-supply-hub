import { useEffect } from 'react';
import { useFormik } from 'formik';
import { isEmpty } from 'lodash';
import { getValidationSchemaForStep } from './validationSchemas';
import { claimIntroRoute } from '../../../util/constants';

export const usePrefetchClaimData = (
    fetchCountries,
    fetchFacilityProcessingType,
    fetchParentCompanies,
    fetchProductionLocation,
    osID,
    productionLocationData,
    countriesOptions,
    facilityProcessingTypeOptions,
    parentCompanyOptions,
) => {
    useEffect(() => {
        if (!countriesOptions || isEmpty(countriesOptions)) {
            fetchCountries();
        }
    }, [countriesOptions, fetchCountries]);

    useEffect(() => {
        if (
            !facilityProcessingTypeOptions ||
            isEmpty(facilityProcessingTypeOptions)
        ) {
            fetchFacilityProcessingType();
        }
    }, [facilityProcessingTypeOptions, fetchFacilityProcessingType]);

    useEffect(() => {
        if (!parentCompanyOptions) {
            fetchParentCompanies();
        }
    }, [parentCompanyOptions, fetchParentCompanies]);

    useEffect(() => {
        if (osID && isEmpty(productionLocationData)) {
            fetchProductionLocation(osID);
        }
    }, [osID, productionLocationData, fetchProductionLocation]);
};

/**
 * Hook to ensure user accessed form through intro page.
 * Redirects to intro page if accessed directly via URL.
 */
export const useRequireIntroAccess = (history, osID) => {
    useEffect(() => {
        const hasAccessedFromIntro = sessionStorage.getItem(
            `claim-form-access-${osID}`,
        );

        if (!hasAccessedFromIntro) {
            history.replace(claimIntroRoute.replace(':osID', osID));
        }

        // Clean up session storage when component unmounts.
        return () => {
            sessionStorage.removeItem(`claim-form-access-${osID}`);
        };
    }, [history, osID]);
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

    /**
     * Re-validate when step changes to restore errors.
     * Without this, returning to a step with invalid data via Continue button
     * will not show errors because Formik clears errors when validationSchema
     * changes.
     */
    useEffect(() => {
        const schema = getValidationSchemaForStep(activeStep);
        const currentStepFields = Object.keys(schema.describe().fields);

        // Mark fields with values as touched when returning to a step.
        const fieldsToTouch = {};
        console.log('currentStepFields', currentStepFields);
        currentStepFields.forEach(field => {
            if (formik.values[field] && formik.values[field] !== '') {
                fieldsToTouch[field] = true;
            }
        });

        if (Object.keys(fieldsToTouch).length > 0) {
            formik.setTouched(fieldsToTouch);
        }
        console.log('fieldsToTouch', fieldsToTouch);

        // Validate to populate errors for current step.
        formik.validateForm();
    }, [activeStep]);

    // Custom field change handler that syncs to Redux.
    const handleFieldChange = (field, value) => {
        formik.setFieldValue(field, value);
        formik.setFieldTouched(field, true, false);
        updateField({ field, value });
    };

    const handleBlur = field => {
        formik.setFieldTouched(field, true);
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
        console.log(
            'hasInteractedWithCurrentStep',
            hasInteractedWithCurrentStep,
        );
        console.log('hasCurrentStepErrors', hasCurrentStepErrors);
        console.log('currentStepFields', currentStepFields);
        // Only disable button if user has interacted AND there are errors.
        return hasInteractedWithCurrentStep && hasCurrentStepErrors;
    };

    return {
        claimForm: formik,
        handleFieldChange,
        handleBlur,
        isButtonDisabled: getButtonDisabledState(),
    };
};
