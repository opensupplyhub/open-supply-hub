import React from 'react';
import { connect } from 'react-redux';
import { bool, func, number, object, arrayOf, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
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
import ErrorState from './ErrorState/ErrorState';
import RequireAuthNotice from '../../RequireAuthNotice';

import {
    fetchClaimFormData,
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
} from '../../../actions/claimForm';

import {
    CLAIM_FORM_STEPS,
    STEP_NAMES,
    STEP_DESCRIPTIONS,
    NEXT_BUTTON_TEXT,
} from './constants';
import { getValidationSchemaForStep } from './validationSchemas';
import claimFormStyles from './styles';
import { isFirstStep, isLastStep, getNextStep, getPreviousStep } from './utils';
import { usePrefetchData, useClaimForm } from './hooks';
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
    userHasSignedIn,
    fetchData,
    setStep,
    markComplete,
    updateField,
}) => {
    // Prefetch data on mount.
    usePrefetchData(fetchData, osID);

    // Handle form submission.
    const handleSubmit = values => {
        // Mark final step as complete.
        markComplete(activeStep);

        // TODO: Implement actual form submission.
        console.log('Form submitted with values:', values);

        // For now, just show a success message.
        alert('Claim form submitted successfully! (This is a placeholder)');
    };

    // Initialize form with custom hook with Formik inside.
    const { claimForm, handleFieldChange, isButtonDisabled } = useClaimForm(
        formData,
        activeStep,
        updateField,
        handleSubmit,
    );

    // Check authentication.
    if (!userHasSignedIn) {
        return (
            <RequireAuthNotice
                title="Claim this production location"
                text="Log in to claim a production location on Open Supply Hub"
            />
        );
    }

    // Show loading state.
    if (fetching && !prefetchedData.facilityData) {
        return (
            <div className={classes.loadingContainer}>
                <CircularProgress />
            </div>
        );
    }

    // Show error state.
    if (error) {
        return <ErrorState error={error} onRetry={() => fetchData(osID)} />;
    }

    const currentStepComponent = stepComponents[activeStep];
    const StepComponent = currentStepComponent || EligibilityStep;

    const handleNext = async () => {
        // Get all fields from current step's validation schema.
        const schema = getValidationSchemaForStep(activeStep);
        const schemaFields = schema.describe().fields;

        // Mark all fields in current step as touched to show validation errors.
        const touchedFields = Object.keys(schemaFields).reduce((acc, field) => {
            acc[field] = true;
            return acc;
        }, {});

        claimForm.setTouched({ ...claimForm.touched, ...touchedFields });

        // Validate only the current step's fields, not the entire form.
        try {
            await schema.validate(claimForm.values, { abortEarly: false });
            // If validation passes, proceed to next step.
            markComplete(activeStep);
            const nextStepIndex = getNextStep(activeStep);
            setStep(nextStepIndex);
        } catch (validationErrors) {
            // Validation failed for current step, stay on this step.
            // Errors will be displayed via Formik's error state.
        }
    };

    const handleBack = () => {
        if (isFirstStep(activeStep)) {
            // Go back to claim intro page.
            history.push(claimIntroRoute.replace(':osID', osID));
        } else {
            const prevStepIndex = getPreviousStep(activeStep);
            setStep(prevStepIndex);
        }
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
                <form onSubmit={claimForm.handleSubmit}>
                    <Paper className={classes.paper}>
                        <Typography
                            variant="title"
                            className={classes.sectionTitle}
                        >
                            {STEP_NAMES[activeStep]}
                        </Typography>
                        <Typography className={classes.sectionDescription}>
                            {STEP_DESCRIPTIONS[activeStep]}
                        </Typography>
                        <StepComponent
                            formData={claimForm.values}
                            handleChange={handleFieldChange}
                            handleBlur={claimForm.handleBlur}
                            errors={claimForm.errors}
                            touched={claimForm.touched}
                            prefetchedData={prefetchedData}
                        />
                        <Grid container className={classes.navigationButtons}>
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
                                        onClick={handleNext}
                                        className={classes.buttonPrimary}
                                        disabled={isButtonDisabled}
                                    >
                                        {NEXT_BUTTON_TEXT[activeStep]}
                                    </Button>
                                )}
                                {isLastStep(activeStep) && (
                                    <Button
                                        variant="contained"
                                        type="submit"
                                        className={classes.buttonPrimary}
                                        disabled={isButtonDisabled}
                                    >
                                        Submit Claim
                                    </Button>
                                )}
                            </Grid>
                        </Grid>
                    </Paper>
                </form>
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
