import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { bool, func, number, object, arrayOf, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { Formik, Form } from 'formik';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import ClaimFormStepper from './Stepper/Stepper';
import EligibilityStep from './Steps/EligibilityStep';
import ContactStep from './Steps/ContactStep';
import BusinessStep from './Steps/BusinessStep';
import ProfileStep from './Steps/ProfileStep';
import RequireAuthNotice from '../../RequireAuthNotice';

import {
    fetchClaimFormData,
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
} from '../../../actions/claimForm';
import {
    fetchCountryOptions,
    fetchSectorOptions,
    fetchFacilityProcessingTypeOptions,
} from '../../../actions/filterOptions';

import {
    CLAIM_FORM_STEPS,
    STEP_NAMES,
    STEP_DESCRIPTIONS,
    NEXT_BUTTON_TEXT,
} from './constants';
import { getValidationSchemaForStep } from './validationSchemas';
import claimFormStyles from './styles';
import { isFirstStep, isLastStep, getNextStep, getPreviousStep } from './utils';
import { useStepResetOnMount, usePrefetchData } from './hooks';
import { claimIntroRoute } from '../../../util/constants';

const stepComponents = {
    [CLAIM_FORM_STEPS.ELIGIBILITY]: EligibilityStep,
    [CLAIM_FORM_STEPS.CONTACT]: ContactStep,
    [CLAIM_FORM_STEPS.BUSINESS]: BusinessStep,
    [CLAIM_FORM_STEPS.PROFILE]: ProfileStep,
};

const ClaimForm = ({
    classes,
    match: {
        params: { osID },
    },
    history,
    activeStep,
    completedSteps,
    formData,
    prefetchedData,
    fetching,
    error,
    countryOptions,
    sectorOptions,
    processingTypeOptions,
    userHasSignedIn,
    fetchData,
    fetchCountries,
    fetchSectors,
    fetchProcessingTypes,
    setStep,
    markComplete,
    updateField,
}) => {
    // Reset to first step on mount
    useStepResetOnMount(setStep);

    // Prefetch data on mount
    usePrefetchData(fetchData, osID);

    // Fetch all dropdown options on mount
    useEffect(() => {
        if (!countryOptions) {
            fetchCountries();
        }
        if (!sectorOptions) {
            fetchSectors();
        }
        if (!processingTypeOptions) {
            fetchProcessingTypes();
        }
    }, [
        countryOptions,
        sectorOptions,
        processingTypeOptions,
        fetchCountries,
        fetchSectors,
        fetchProcessingTypes,
    ]);

    // Check authentication
    if (!userHasSignedIn) {
        return (
            <RequireAuthNotice
                title="Claim this production location"
                text="Log in to claim a production location on Open Supply Hub"
            />
        );
    }

    // Show loading state
    if (fetching && !prefetchedData.facilityData) {
        return (
            <div className={classes.loadingContainer}>
                <CircularProgress />
            </div>
        );
    }

    // Show error state
    if (error) {
        return (
            <div className={classes.container}>
                <Paper className={classes.paper}>
                    <div className={classes.errorContainer}>
                        <Typography
                            variant="title"
                            className={classes.errorText}
                        >
                            An error occurred while loading the claim form
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                            {error}
                        </Typography>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={() => fetchData(osID)}
                            className={classes.errorButton}
                        >
                            Try Again
                        </Button>
                    </div>
                </Paper>
            </div>
        );
    }

    const currentStepComponent = stepComponents[activeStep];
    const StepComponent = currentStepComponent || EligibilityStep;

    const handleNext = async (validateForm, values) => {
        const errors = await validateForm(values);

        if (Object.keys(errors).length === 0) {
            markComplete(activeStep);
            const nextStepIndex = getNextStep(activeStep);
            setStep(nextStepIndex);
        }
    };

    const handleBack = () => {
        if (isFirstStep(activeStep)) {
            // Go back to claim intro page
            history.push(claimIntroRoute.replace(':osID', osID));
        } else {
            const prevStepIndex = getPreviousStep(activeStep);
            setStep(prevStepIndex);
        }
    };

    const handleSubmit = values => {
        // Mark final step as complete
        markComplete(activeStep);

        // TODO: Implement actual form submission
        // eslint-disable-next-line no-console
        console.log('Form submitted with values:', values);

        // For now, just show a success message
        // eslint-disable-next-line no-alert
        alert('Claim form submitted successfully! (This is a placeholder)');
    };

    const handleFieldChange = (field, value, setFieldValue) => {
        setFieldValue(field, value);
        updateField({ field, value });
    };

    return (
        <div className={classes.container}>
            <div className={classes.innerContainer}>
                <Typography className={classes.title}>
                    Production Location Claims Process
                </Typography>
                <Typography className={classes.description}>
                    Complete all sections to submit your production location
                    claim
                </Typography>
                <ClaimFormStepper
                    currentStep={activeStep}
                    completedSteps={completedSteps}
                    onStepClick={setStep}
                />
                <Formik
                    initialValues={formData}
                    validationSchema={getValidationSchemaForStep(activeStep)}
                    enableReinitialize
                    onSubmit={handleSubmit}
                >
                    {({
                        values,
                        errors,
                        touched,
                        setFieldValue,
                        validateForm,
                    }) => (
                        <Form>
                            <Paper className={classes.paper}>
                                <Typography
                                    variant="title"
                                    className={classes.sectionTitle}
                                >
                                    {STEP_NAMES[activeStep]}
                                </Typography>
                                <Typography
                                    className={classes.sectionDescription}
                                >
                                    {STEP_DESCRIPTIONS[activeStep]}
                                </Typography>
                                <StepComponent
                                    formData={values}
                                    handleChange={(field, value) =>
                                        handleFieldChange(
                                            field,
                                            value,
                                            setFieldValue,
                                        )
                                    }
                                    errors={errors}
                                    touched={touched}
                                    prefetchedData={prefetchedData}
                                    countryOptions={countryOptions}
                                    sectorOptions={sectorOptions}
                                    processingTypeOptions={
                                        processingTypeOptions
                                    }
                                />
                                <Grid
                                    container
                                    className={classes.navigationButtons}
                                >
                                    <Grid item>
                                        <Button
                                            variant="outlined"
                                            onClick={handleBack}
                                            className={classes.buttonBack}
                                        >
                                            {isFirstStep(activeStep)
                                                ? 'Go Back'
                                                : 'Back'}
                                        </Button>
                                    </Grid>
                                    <Grid item>
                                        {!isLastStep(activeStep) && (
                                            <Button
                                                variant="contained"
                                                onClick={() =>
                                                    handleNext(
                                                        validateForm,
                                                        values,
                                                    )
                                                }
                                                className={
                                                    classes.buttonPrimary
                                                }
                                            >
                                                {NEXT_BUTTON_TEXT[activeStep]}
                                            </Button>
                                        )}
                                        {isLastStep(activeStep) && (
                                            <Button
                                                variant="contained"
                                                type="submit"
                                                className={
                                                    classes.buttonPrimary
                                                }
                                            >
                                                Submit Claim
                                            </Button>
                                        )}
                                    </Grid>
                                </Grid>
                            </Paper>
                        </Form>
                    )}
                </Formik>
            </div>
        </div>
    );
};

ClaimForm.defaultProps = {
    error: null,
};

ClaimForm.propTypes = {
    classes: object.isRequired,
    match: object.isRequired,
    history: object.isRequired,
    activeStep: number.isRequired,
    completedSteps: arrayOf(number).isRequired,
    formData: object.isRequired,
    prefetchedData: object.isRequired,
    fetching: bool.isRequired,
    error: string,
    countryOptions: object.isRequired,
    sectorOptions: object.isRequired,
    processingTypeOptions: object.isRequired,
    userHasSignedIn: bool.isRequired,
    fetchData: func.isRequired,
    fetchCountries: func.isRequired,
    fetchSectors: func.isRequired,
    fetchProcessingTypes: func.isRequired,
    setStep: func.isRequired,
    markComplete: func.isRequired,
    updateField: func.isRequired,
};

const mapStateToProps = ({
    claimForm: {
        activeStep,
        completedSteps,
        formData,
        prefetchedData,
        fetching,
        error,
    },
    filterOptions: {
        countries: { data: countryOptions },
        sectors: { data: sectorOptions },
        facilityProcessingType: { data: processingTypeOptions },
    },
    auth: {
        user: { user },
    },
}) => ({
    activeStep,
    completedSteps,
    formData,
    prefetchedData,
    fetching,
    error,
    countryOptions,
    sectorOptions,
    processingTypeOptions,
    userHasSignedIn: !user.isAnon,
});

const mapDispatchToProps = dispatch => ({
    fetchData: osID => dispatch(fetchClaimFormData(osID)),
    fetchCountries: () => dispatch(fetchCountryOptions()),
    fetchSectors: () => dispatch(fetchSectorOptions()),
    fetchProcessingTypes: () => dispatch(fetchFacilityProcessingTypeOptions()),
    setStep: stepIndex => dispatch(setActiveClaimFormStep(stepIndex)),
    markComplete: stepIndex => dispatch(markStepComplete(stepIndex)),
    updateField: payload => dispatch(updateClaimFormField(payload)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimFormStyles)(ClaimForm));
