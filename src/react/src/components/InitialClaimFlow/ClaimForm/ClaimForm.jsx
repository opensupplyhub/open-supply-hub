import React from 'react';
import { connect } from 'react-redux';
import { bool, func, number, object, arrayOf, array } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import Security from '@material-ui/icons/Security';
import People from '@material-ui/icons/People';
import Language from '@material-ui/icons/Language';
import Business from '@material-ui/icons/Business';

import ClaimFormStepper from './Stepper/Stepper';
import EligibilityStep from './Steps/EligibilityStep/EligibilityStep';
import ContactStep from './Steps/ContactStep';
import BusinessStep from './Steps/BusinessStep';
import ProfileStep from './Steps/ProfileStep';
import ErrorState from './ErrorState/ErrorState';
import RequireAuthNotice from '../../RequireAuthNotice';

import {
    setActiveClaimFormStep,
    markStepComplete,
    updateClaimFormField,
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
import claimFormStyles from './styles';
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
}) => {
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

    // Handle form submission.
    const handleSubmit = values => {
        // Mark final step as complete.
        markComplete(activeStep);

        // TODO: Create action in the claimForm.js to submit the form data to
        // the backend via api/facilities/{os_id}/claim/ POST endpoint.
        console.log('Form submitted with values:', values);
        alert('Claim form submitted successfully! (This is a placeholder)');
    };

    // Initialize form with custom hook with Formik inside.
    const {
        claimForm,
        handleFieldChange,
        handleBlur,
        isButtonDisabled,
    } = useClaimForm(formData, activeStep, updateField, handleSubmit);

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

        // Use Formik's validateForm and rely on the returned latest errors.
        const latestErrors = await claimForm.validateForm();

        // Proceed only if the CURRENT STEP has no errors.
        const hasCurrentStepErrors = Object.keys(schemaFields).some(
            field => latestErrors && latestErrors[field],
        );

        if (!hasCurrentStepErrors) {
            markComplete(activeStep);
            const nextStepIndex = getNextStep(activeStep);
            setStep(nextStepIndex);
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
};

const mapStateToProps = ({
    claimForm: { activeStep, completedSteps, formData },
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
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimFormStyles)(ClaimForm));
