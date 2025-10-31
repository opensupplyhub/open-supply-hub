import React, { useState, useEffect } from 'react';
import { connect } from 'react-redux';
import { bool, func, number, object, arrayOf, array } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Security from '@material-ui/icons/Security';
import People from '@material-ui/icons/People';
import Language from '@material-ui/icons/Language';
import Business from '@material-ui/icons/Business';

import ClaimFormStepper from './Stepper/Stepper';
import EligibilityStep from './Steps/EligibilityStep/EligibilityStep';
import ContactStep from './Steps/ContactStep';
import BusinessStep from './Steps/BusinessStep';
import ProfileStep from './Steps/ProfileStep/ProfileStep';
import ErrorState from './ErrorState/ErrorState';
import RequireAuthNotice from '../../RequireAuthNotice';

import {
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
    submitClaimFormData,
} from '../../../actions/claimForm';
import {
    fetchCountryOptions,
    fetchFacilityProcessingTypeOptions,
    fetchParentCompanyOptions,
} from '../../../actions/filterOptions';
import { fetchProductionLocationByOsId } from '../../../actions/contributeProductionLocation';

import {
    CLAIM_FORM_STEPS,
    STEP_NAMES,
    STEP_DESCRIPTIONS,
    NEXT_BUTTON_TEXT,
    STEP_ICONS,
} from './constants';
import { getValidationSchemaForStep } from './validationSchemas';
import { claimFormStyles, popupDialogStyles } from './styles';
import {
    isFirstStep,
    isLastStep,
    getNextStep,
    getPreviousStep,
    getPrefetchErrorConfig,
} from './utils';
import {
    usePrefetchClaimData,
    useClaimForm,
    useRequireIntroAccess,
} from './hooks';
import { claimIntroRoute } from '../../../util/constants';
import COLOURS from '../../../util/COLOURS';

const iconMapping = {
    Security,
    People,
    Language,
    Business,
};

const getIconComponent = iconName => iconMapping[iconName] || Security;

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
    submissionFetching,
    submissionError,
    countriesOptions,
    facilityProcessingTypeOptions,
    parentCompanyOptions,
    productionLocationData,
    countriesFetching,
    facilityProcessingTypeFetching,
    parentCompaniesFetching,
    productionLocationFetching,
    countriesError,
    facilityProcessingTypeError,
    parentCompaniesError,
    productionLocationError,
    userHasSignedIn,
    fetchCountries,
    fetchFacilityProcessingType,
    fetchParentCompanies,
    fetchProductionLocation,
    setStep,
    markComplete,
    updateField,
    submitClaim,
}) => {
    // Track emissions validation errors from ProfileStep.
    const [emissionsHasErrors, setEmissionsHasErrors] = useState(false);

    // Track dialog state for success popup.
    const [dialogIsOpen, setDialogIsOpen] = useState(false);
    const [submittingForm, setSubmittingForm] = useState(false);

    // Redirect to intro page if user accessed form directly via URL.
    useRequireIntroAccess(history, osID);

    // Prefetch required data on mount.
    usePrefetchClaimData(
        fetchCountries,
        fetchFacilityProcessingType,
        fetchParentCompanies,
        fetchProductionLocation,
        osID,
        productionLocationData,
        countriesOptions,
        facilityProcessingTypeOptions,
        parentCompanyOptions,
    );

    // Show success dialog when submission completes.
    useEffect(() => {
        if (submissionFetching) {
            setSubmittingForm(true);
        }
        if (submittingForm && !submissionFetching && !submissionError) {
            setSubmittingForm(false);
            setDialogIsOpen(true);
        }
    }, [submittingForm, submissionFetching, submissionError]);

    // Handle form submission.
    const handleSubmit = () => {
        markComplete(activeStep);
        submitClaim(osID, emissionsHasErrors);
    };

    // Initialize form with custom hook with Formik inside.
    const {
        claimForm,
        handleFieldChange,
        handleBlur,
        isButtonDisabled,
    } = useClaimForm(
        formData,
        activeStep,
        updateField,
        handleSubmit,
        emissionsHasErrors,
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

    // Show loading state while prefetching data.
    const isPrefetching =
        countriesFetching ||
        facilityProcessingTypeFetching ||
        parentCompaniesFetching ||
        productionLocationFetching;

    if (isPrefetching) {
        return (
            <div className={classes.loadingContainer}>
                <CircularProgress />
            </div>
        );
    }

    // Show error state if prefetching failed.
    const errorConfig = getPrefetchErrorConfig(
        {
            countriesError,
            facilityProcessingTypeError,
            parentCompaniesError,
            productionLocationError,
        },
        {
            fetchCountries,
            fetchFacilityProcessingType,
            fetchParentCompanies,
            fetchProductionLocation,
            osID,
        },
    );

    if (errorConfig) {
        return (
            <ErrorState
                error={errorConfig.message}
                onRetry={errorConfig.onRetry}
            />
        );
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
                            className={classes.titleStyles}
                        >
                            {(() => {
                                const IconName = getIconComponent(
                                    STEP_ICONS[activeStep],
                                );
                                return <IconName />;
                            })()}
                            {STEP_NAMES[activeStep]}
                        </Typography>
                        <Typography className={classes.sectionDescription}>
                            {STEP_DESCRIPTIONS[activeStep]}
                        </Typography>
                        <StepComponent
                            formData={claimForm.values}
                            handleChange={handleFieldChange}
                            handleBlur={handleBlur}
                            errors={claimForm.errors}
                            touched={claimForm.touched}
                            countryOptions={countriesOptions}
                            processingTypeOptions={
                                facilityProcessingTypeOptions
                            }
                            parentCompanyOptions={parentCompanyOptions}
                            onEmissionsValidationChange={setEmissionsHasErrors}
                        />
                        {submissionError && (
                            <Typography
                                variant="body2"
                                color="error"
                                style={{
                                    textAlign: 'center',
                                    marginTop: '24px',
                                    fontSize: '16px',
                                }}
                            >
                                An error prevented submitting the form
                            </Typography>
                        )}
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

            <Dialog open={dialogIsOpen}>
                {dialogIsOpen && (
                    <div style={popupDialogStyles.containerStyles}>
                        <DialogContent>
                            <Typography
                                variant="title"
                                style={popupDialogStyles.titleStyles}
                            >
                                Thank you for submitting your claim request!
                            </Typography>
                            <Typography style={popupDialogStyles.contentStyles}>
                                You will receive a notification once it has been
                                reviewed.
                            </Typography>
                            <hr
                                style={{
                                    color: COLOURS.GREY,
                                    backgroundColor: COLOURS.GREY,
                                    height: 1,
                                }}
                            />
                        </DialogContent>
                        <DialogActions style={popupDialogStyles.actionStyles}>
                            <Button
                                variant="contained"
                                color="primary"
                                href="/claimed"
                                className={classes.popupButtonStyles}
                            >
                                View My Approved Claims
                            </Button>
                            <Button
                                variant="contained"
                                color="primary"
                                href="/"
                                className={classes.popupButtonStyles}
                            >
                                Search OS Hub
                            </Button>
                        </DialogActions>
                    </div>
                )}
            </Dialog>
        </div>
    );
};

ClaimForm.defaultProps = {
    submissionError: null,
    countriesOptions: [],
    facilityProcessingTypeOptions: [],
    parentCompanyOptions: [],
    productionLocationData: {},
    countriesError: null,
    facilityProcessingTypeError: null,
    parentCompaniesError: null,
    productionLocationError: null,
};

ClaimForm.propTypes = {
    classes: object.isRequired,
    match: object.isRequired,
    history: object.isRequired,
    activeStep: number.isRequired,
    completedSteps: arrayOf(number).isRequired,
    formData: object.isRequired,
    submissionFetching: bool.isRequired,
    submissionError: array,
    countriesOptions: array,
    facilityProcessingTypeOptions: array,
    parentCompanyOptions: array,
    productionLocationData: object,
    countriesFetching: bool.isRequired,
    facilityProcessingTypeFetching: bool.isRequired,
    parentCompaniesFetching: bool.isRequired,
    productionLocationFetching: bool.isRequired,
    countriesError: array,
    facilityProcessingTypeError: array,
    parentCompaniesError: array,
    productionLocationError: array,
    userHasSignedIn: bool.isRequired,
    fetchCountries: func.isRequired,
    fetchFacilityProcessingType: func.isRequired,
    fetchParentCompanies: func.isRequired,
    fetchProductionLocation: func.isRequired,
    setStep: func.isRequired,
    markComplete: func.isRequired,
    updateField: func.isRequired,
    submitClaim: func.isRequired,
};

const mapStateToProps = ({
    claimForm: { activeStep, completedSteps, formData, submissionState },
    filterOptions: {
        countries: {
            data: countriesOptions,
            fetching: countriesFetching,
            error: countriesError,
        },
        facilityProcessingType: {
            data: facilityProcessingTypeOptions,
            fetching: facilityProcessingTypeFetching,
            error: facilityProcessingTypeError,
        },
        parentCompanies: {
            data: parentCompanyOptions,
            fetching: parentCompaniesFetching,
            error: parentCompaniesError,
        },
    },
    contributeProductionLocation: {
        singleProductionLocation: {
            data: productionLocationData,
            fetching: productionLocationFetching,
            error: productionLocationError,
        },
    },
    auth: {
        user: { user },
    },
}) => ({
    activeStep,
    completedSteps,
    formData,
    submissionFetching: submissionState.fetching,
    submissionError: submissionState.error,
    countriesOptions,
    facilityProcessingTypeOptions,
    parentCompanyOptions,
    countriesFetching,
    facilityProcessingTypeFetching,
    parentCompaniesFetching,
    productionLocationFetching,
    productionLocationData,
    countriesError,
    facilityProcessingTypeError,
    parentCompaniesError,
    productionLocationError,
    userHasSignedIn: !user.isAnon,
});

const mapDispatchToProps = dispatch => ({
    fetchCountries: () => dispatch(fetchCountryOptions()),
    fetchFacilityProcessingType: () =>
        dispatch(fetchFacilityProcessingTypeOptions()),
    fetchParentCompanies: () => dispatch(fetchParentCompanyOptions()),
    fetchProductionLocation: osID =>
        dispatch(fetchProductionLocationByOsId(osID)),
    setStep: stepIndex => dispatch(setActiveClaimFormStep(stepIndex)),
    markComplete: stepIndex => dispatch(markStepComplete(stepIndex)),
    updateField: payload => dispatch(updateClaimFormField(payload)),
    submitClaim: (osID, emissionsHasErrors) =>
        dispatch(submitClaimFormData(osID, emissionsHasErrors)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimFormStyles)(ClaimForm));
