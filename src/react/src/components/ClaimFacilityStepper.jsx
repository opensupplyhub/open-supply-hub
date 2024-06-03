import React, { useState, useEffect } from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import clamp from 'lodash/clamp';
import last from 'lodash/last';
import stubTrue from 'lodash/stubTrue';

import BadgeClaimed from './BadgeClaimed';
import ClaimFacilityIntroStep from './ClaimFacilityIntroStep';
// import ClaimFacilityContactInfoStep from './ClaimFacilityContactInfoStep';
// import ClaimFacilitySupportDocs from './ClaimFacilitySupportDocs';
import ClaimFacilityAdditionalData from './ClaimFacilityAdditionalData';
import ClaimFacilityFacilityInfoStep from './ClaimFacilityFacilityInfoStep';
import ClaimFacilityVerificationInfoStep from './ClaimFacilityVerificationInfoStep';
import ClaimFacilityConfirmationStep from './ClaimFacilityConfirmationStep';

import { submitClaimAFacilityData } from '../actions/claimFacility';

import COLOURS from '../util/COLOURS';

import {
    // claimFacilityContactInfoStepIsValid,
    // claimFacilitySupportDocsIsValid,
    claimFacilityFacilityInfoStepIsValid,
    claimAFacilityFormIsValid,
} from '../util/util';

const claimFacilityStepperStyles = Object.freeze({
    containerStyles: Object.freeze({
        padding: '10px 20px 5px',
    }),
    buttonsContainerStyles: Object.freeze({
        padding: '24px 0',
    }),
    buttonStyles: Object.freeze({
        margin: '10px',
    }),
    formContainerStyles: Object.freeze({
        width: '100%',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
    }),
    validationMessageStyles: Object.freeze({
        padding: '5px 0',
    }),
});

const SUBMIT_FORM = 'SUBMIT_FORM';

const steps = Object.freeze([
    Object.freeze({
        name: 'Claim this facility',
        component: ClaimFacilityIntroStep,
        next: 'Contact Information',
        hasBackButton: false,
        hasNextButton: true,
        stepInputIsValid: stubTrue,
    }),
    Object.freeze({
        name: 'Contact Information',
        component: ClaimFacilityAdditionalData,
        next: 'Facility Information',
        hasBackButton: true,
        hasNextButton: true,
        stepInputIsValid: stubTrue,
    }),
    Object.freeze({
        name: 'Facility Information',
        component: ClaimFacilityFacilityInfoStep,
        next: 'Verification Information',
        hasBackButton: true,
        hasNextButton: true,
        stepInputIsValid: claimFacilityFacilityInfoStepIsValid,
    }),
    Object.freeze({
        name: 'Verification Information',
        component: ClaimFacilityVerificationInfoStep,
        next: 'Submit Facility Claim',
        hasBackButton: true,
        hasNextButton: true,
        nextButtonAction: SUBMIT_FORM,
        stepInputIsValid: claimAFacilityFormIsValid,
    }),
    Object.freeze({
        name: 'Submitted Successfully',
        component: ClaimFacilityConfirmationStep,
        next: null,
        hasBackButton: false,
        hasNextButton: false,
    }),
]);

function ClaimFacilityStepper({ fetching, submitClaimForm, formData, error }) {
    const [activeStep, setActiveStep] = useState(0);
    const [submittingForm, setSubmittingForm] = useState(false);

    const incrementActiveStep = () =>
        setActiveStep(clamp(activeStep + 1, 0, steps.length));
    const decrementActiveStep = () =>
        setActiveStep(clamp(activeStep - 1, 0, steps.length));

    const {
        component: ActiveStepComponent,
        next: nextStepName,
        name: activeStepName,
        hasBackButton,
        hasNextButton,
        nextButtonAction,
        stepInputIsValid,
    } = steps[activeStep];

    useEffect(() => {
        if (fetching) {
            setSubmittingForm(true);
        } else if (
            nextButtonAction === SUBMIT_FORM &&
            !fetching &&
            !error &&
            submittingForm
        ) {
            setSubmittingForm(false);
            setActiveStep(activeStep + 1);
        }
    }, [
        submittingForm,
        setSubmittingForm,
        nextButtonAction,
        activeStep,
        setActiveStep,
        error,
        fetching,
    ]);

    const { name: lastStepName } = last(steps);

    const controlsSection =
        activeStepName !== lastStepName ? (
            <>
                <div style={claimFacilityStepperStyles.formContainerStyles}>
                    <Typography variant="title">
                        {nextButtonAction !== SUBMIT_FORM
                            ? `Step ${activeStep + 2}: ${nextStepName}`
                            : nextStepName}
                    </Typography>
                    {error || !stepInputIsValid(formData) ? (
                        <Typography
                            variant="body2"
                            style={
                                claimFacilityStepperStyles.validationMessageStyles
                            }
                            color="error"
                        >
                            {error
                                ? 'An error prevented submitting the form'
                                : 'Some required fields are missing or invalid.'}
                        </Typography>
                    ) : null}
                    <div
                        style={
                            claimFacilityStepperStyles.buttonsContainerStyles
                        }
                    >
                        {hasBackButton && (
                            <Button
                                color="default"
                                variant="outlined"
                                onClick={decrementActiveStep}
                                style={claimFacilityStepperStyles.buttonStyles}
                                disabled={activeStep === 0}
                            >
                                Back
                            </Button>
                        )}
                        {hasNextButton && nextButtonAction !== SUBMIT_FORM && (
                            <Button
                                color="primary"
                                variant="contained"
                                onClick={incrementActiveStep}
                                style={claimFacilityStepperStyles.buttonStyles}
                                disabled={!stepInputIsValid(formData)}
                            >
                                Next
                            </Button>
                        )}
                        {hasNextButton && nextButtonAction === SUBMIT_FORM && (
                            <Button
                                color="primary"
                                variant="contained"
                                onClick={submitClaimForm}
                                style={claimFacilityStepperStyles.buttonStyles}
                                disabled={
                                    fetching ||
                                    !claimAFacilityFormIsValid(formData)
                                }
                            >
                                {fetching ? (
                                    <CircularProgress size={5} />
                                ) : (
                                    'Submit'
                                )}
                            </Button>
                        )}
                    </div>
                </div>
            </>
        ) : null;

    return (
        <div style={claimFacilityStepperStyles.containerStyles}>
            <Stepper activeStep={activeStep}>
                {steps.map(({ name }, index) => (
                    <Step key={name}>
                        {name === lastStepName ? (
                            <StepLabel
                                icon={
                                    <BadgeClaimed
                                        color={
                                            activeStepName === lastStepName
                                                ? COLOURS.NAVY_BLUE
                                                : COLOURS.GREY
                                        }
                                    />
                                }
                            >
                                {activeStep === index ? name : ''}
                            </StepLabel>
                        ) : (
                            <StepLabel>
                                {activeStep === index ? name : ''}
                            </StepLabel>
                        )}
                    </Step>
                ))}
            </Stepper>
            <div style={claimFacilityStepperStyles.formContainerStyles}>
                <ActiveStepComponent />
            </div>
            {controlsSection}
        </div>
    );
}

ClaimFacilityStepper.defaultProps = {
    error: null,
};

ClaimFacilityStepper.propTypes = {
    fetching: bool.isRequired,
    submitClaimForm: func.isRequired,
    formData: shape({
        companyName: string.isRequired,
        contactPerson: string.isRequired,
        phoneNumber: string.isRequired,
    }).isRequired,
    error: arrayOf(string),
};

function mapStateToProps({
    claimFacility: {
        claimData: { fetching, formData, error },
    },
}) {
    return {
        fetching,
        formData,
        error,
    };
}

function mapDispatchToProps(
    dispatch,
    {
        match: {
            params: { osID },
        },
    },
) {
    return {
        submitClaimForm: () => dispatch(submitClaimAFacilityData(osID)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimFacilityStepper);
