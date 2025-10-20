import React from 'react';
import { connect } from 'react-redux';
import { bool, func, number, object, arrayOf, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { Formik, Form } from 'formik';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import LinearProgress from '@material-ui/core/LinearProgress';
import ArrowBack from '@material-ui/icons/ArrowBack';
import ArrowForward from '@material-ui/icons/ArrowForward';

import ClaimFormStepper from './Stepper/Stepper';
import EligibilityStep from './Steps/EligibilityStep';
import ContactStep from './Steps/ContactStep';
import BusinessStep from './Steps/BusinessStep';
import ProfileStep from './Steps/ProfileStep';
import RequireAuthNotice from '../RequireAuthNotice';

import {
    fetchClaimFormData,
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
} from '../../actions/claimForm';

import {
    CLAIM_FORM_STEPS,
    STEP_NAMES,
    STEP_DESCRIPTIONS,
    claimIntroRoute,
} from './constants';
import { getValidationSchemaForStep } from './validationSchemas';
import claimFormStyles from './styles';
import {
    calculateProgress,
    isFirstStep,
    isLastStep,
    getNextStep,
    getPreviousStep,
} from './utils';
import { useStepResetOnMount, usePrefetchData } from './hooks';

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
    userHasSignedIn,
    fetchData,
    setStep,
    markComplete,
    updateField,
}) => {
    // Reset to first step on mount
    useStepResetOnMount(setStep);

    // Prefetch data on mount
    usePrefetchData(fetchData, osID);

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
                        <Typography variant="h6" className={classes.errorText}>
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
    const progress = calculateProgress(completedSteps);

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
                {/* Header */}
                <Typography variant="h5" className={classes.title}>
                    Production Location Claims Process
                </Typography>
                <Typography variant="body2" className={classes.description}>
                    Complete all sections to submit your production location
                    claim
                </Typography>
                <div className={classes.progressContainer}>
                    <LinearProgress
                        variant="determinate"
                        value={progress}
                        className={classes.progressBar}
                    />
                    <Typography
                        variant="caption"
                        className={classes.progressText}
                    >
                        {completedSteps.length} of 4 sections completed
                    </Typography>
                </div>

                {/* Stepper */}
                <ClaimFormStepper
                    currentStep={activeStep}
                    completedSteps={completedSteps}
                    onStepClick={setStep}
                />

                {/* Form */}
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
                                {/* Step Title and Description */}
                                <Typography
                                    variant="h6"
                                    className={classes.sectionTitle}
                                >
                                    {STEP_NAMES[activeStep]}
                                </Typography>
                                <Typography
                                    className={classes.sectionDescription}
                                >
                                    {STEP_DESCRIPTIONS[activeStep]}
                                </Typography>

                                {/* Step Content */}
                                <div className={classes.stepContent}>
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
                                    />
                                </div>

                                {/* Navigation Buttons */}
                                <Grid
                                    container
                                    spacing={16}
                                    justifyContent="space-between"
                                    className={classes.navigationButtons}
                                >
                                    <Grid item>
                                        <Button
                                            variant="outlined"
                                            onClick={handleBack}
                                            startIcon={<ArrowBack />}
                                            className={classes.buttonBack}
                                        >
                                            {isFirstStep(activeStep)
                                                ? 'GO BACK'
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
                                                endIcon={<ArrowForward />}
                                                className={classes.buttonNext}
                                            >
                                                Continue
                                            </Button>
                                        )}
                                        {isLastStep(activeStep) && (
                                            <Button
                                                variant="contained"
                                                type="submit"
                                                className={classes.buttonSubmit}
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
    userHasSignedIn: bool.isRequired,
    fetchData: func.isRequired,
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
    userHasSignedIn: !user.isAnon,
});

const mapDispatchToProps = dispatch => ({
    fetchData: osID => dispatch(fetchClaimFormData(osID)),
    setStep: stepIndex => dispatch(setActiveClaimFormStep(stepIndex)),
    markComplete: stepIndex => dispatch(markStepComplete(stepIndex)),
    updateField: payload => dispatch(updateClaimFormField(payload)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimFormStyles)(ClaimForm));
