import React, { useState, useEffect } from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles, withTheme } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import clamp from 'lodash/clamp';
import constant from 'lodash/constant';

import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';

import ClaimFacilityIntroStep from './ClaimFacilityIntroStep';
import ClaimFacilitySupportDocs from './ClaimFacilitySupportDocs';
import ClaimFacilityAdditionalData from './ClaimFacilityAdditionalData';

import { submitClaimAFacilityData } from '../actions/claimFacility';

import COLOURS from '../util/COLOURS';
import { facilityClaimStepsNames } from '../util/constants';

import {
    claimFacilitySupportDocsIsValid,
    claimAFacilityFormIsValid,
    makeFacilityDetailLink,
} from '../util/util';

const stepperStyles = theme =>
    Object.freeze({
        buttonStyles: Object.freeze({
            margin: '5px',
            width: '20%',
            display: 'flex',
            fontWeight: 'bold',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
        popupButtonStyles: Object.freeze({
            fontWeight: 'bold',
            margin: '10px',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
    });

const popupDialogStyles = Object.freeze({
    containerStyles: Object.freeze({
        padding: '35px',
    }),
    titleStyles: Object.freeze({
        margin: 'auto',
        textAlign: 'center',
        color: COLOURS.NEAR_BLACK,
        paddingBottom: '10px',
        fontSize: '2.125rem',
        fontWeight: '400',
        lineHeight: '1.20588em',
    }),
    contentStyles: Object.freeze({
        fontSize: '20px',
        margin: 'auto',
        textAlign: 'center',
        paddingTop: '10px',
    }),
    actionStyles: Object.freeze({
        justifyContent: 'center',
    }),
});

const claimFacilityStepperStyles = Object.freeze({
    containerStyles: Object.freeze({
        padding: '10px 20px 5px',
    }),
    buttonsContainerStyles: Object.freeze({
        flexDirection: 'column',
    }),
    buttonStyles: Object.freeze({
        margin: '5px',
        width: '20%',
        display: 'flex',
        fontWeight: 'bold',
    }),
    displayNone: Object.freeze({
        display: 'none',
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
    paperStyles: Object.freeze({
        padding: '0 50px 50px 50px',
        width: '100%',
    }),
});

const infoTitleStyle = Object.freeze({
    paddingBottom: '10px',
    paddingLeft: '20px',
    color: COLOURS.NEAR_BLACK,
    fontWeight: 'bold',
});

const infoDescStyle = Object.freeze({
    fontWeight: 'bold',
    paddingBottom: '30px',
    paddingLeft: '20px',
});

const SUBMIT_FORM = 'SUBMIT_FORM';

const steps = Object.freeze([
    Object.freeze({
        name: facilityClaimStepsNames.CLAIM_PROD_LOCATION,
        component: ClaimFacilityIntroStep,
        next: facilityClaimStepsNames.SUPPORT_DOC,
        hasBackButton: true,
        hasNextButton: true,
        stepInputIsValid: ({ agreement }) => agreement === 'yes',
    }),
    Object.freeze({
        name: facilityClaimStepsNames.SUPPORT_DOC,
        component: ClaimFacilitySupportDocs,
        next: facilityClaimStepsNames.ADDITIONAL_DATA,
        hasBackButton: true,
        hasNextButton: true,
        stepInputIsValid: claimFacilitySupportDocsIsValid,
    }),
    Object.freeze({
        name: facilityClaimStepsNames.ADDITIONAL_DATA,
        component: ClaimFacilityAdditionalData,
        next: null,
        hasBackButton: true,
        hasNextButton: true,
        nextButtonAction: SUBMIT_FORM,
        stepInputIsValid: claimAFacilityFormIsValid,
    }),
]);

const InvisibleDiv = constant(<div style={{ display: 'none ' }} />);

function ClaimFacilityStepper({
    fetching,
    submitClaimForm,
    formData,
    error,
    classes,
    match: {
        params: { osID },
    },
}) {
    const [activeStep, setActiveStep] = useState(0);
    const [submittingForm, setSubmittingForm] = useState(false);

    const incrementActiveStep = () =>
        setActiveStep(clamp(activeStep + 1, 0, steps.length));
    const decrementActiveStep = () =>
        setActiveStep(clamp(activeStep - 1, 0, steps.length));

    const [dialogIsOpen, setDialogIsOpen] = useState(false);

    const openDialog = () => {
        setDialogIsOpen(true);
    };

    const {
        component: ActiveStepComponent,
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
            openDialog();
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

    const controlsSection = (
        <>
            <div style={claimFacilityStepperStyles.formContainerStyles}>
                {error ||
                (!stepInputIsValid(formData) &&
                    activeStepName !==
                        facilityClaimStepsNames.CLAIM_PROD_LOCATION) ? (
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
                        formData.agreement === 'yes'
                            ? claimFacilityStepperStyles.buttonsContainerStyles
                            : claimFacilityStepperStyles.displayNone
                    }
                >
                    {hasNextButton && nextButtonAction !== SUBMIT_FORM && (
                        <Button
                            color="secondary"
                            variant="contained"
                            onClick={incrementActiveStep}
                            className={classes.buttonStyles}
                            disabled={!stepInputIsValid(formData)}
                        >
                            Next
                        </Button>
                    )}
                    {hasNextButton && nextButtonAction === SUBMIT_FORM && (
                        <Button
                            color="secondary"
                            variant="contained"
                            onClick={submitClaimForm}
                            className={classes.buttonStyles}
                            disabled={
                                fetching || !claimAFacilityFormIsValid(formData)
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
                <div style={claimFacilityStepperStyles.buttonsContainerStyles}>
                    {hasBackButton && activeStep === 0 && (
                        <Button
                            color="secondary"
                            variant="contained"
                            to={makeFacilityDetailLink(osID)}
                            href={makeFacilityDetailLink(osID)}
                            style={claimFacilityStepperStyles.buttonStyles}
                        >
                            Go Back
                        </Button>
                    )}
                    {hasBackButton && activeStep > 0 && (
                        <Button
                            color="secondary"
                            variant="contained"
                            onClick={decrementActiveStep}
                            style={claimFacilityStepperStyles.buttonStyles}
                        >
                            Go Back
                        </Button>
                    )}
                </div>
            </div>
        </>
    );

    return (
        <div style={claimFacilityStepperStyles.containerStyles}>
            <Dialog open={dialogIsOpen}>
                {dialogIsOpen ? (
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
                ) : (
                    <InvisibleDiv />
                )}
            </Dialog>
            <div style={claimFacilityStepperStyles.formContainerStyles}>
                {activeStepName ===
                facilityClaimStepsNames.CLAIM_PROD_LOCATION ? (
                    <div>
                        <Typography variant="display3" style={infoTitleStyle}>
                            Claim a Production Location
                        </Typography>
                        <Typography variant="subheading" style={infoDescStyle}>
                            In order to submit a claim request, you must be an
                            owner or senior manager of the production location.
                        </Typography>
                    </div>
                ) : null}
                {activeStepName === facilityClaimStepsNames.SUPPORT_DOC ? (
                    <div>
                        <Typography variant="display3" style={infoTitleStyle}>
                            Supporting Documentation
                        </Typography>
                        <Typography variant="subheading" style={infoDescStyle}>
                            Use the form below to complete your claim request.
                        </Typography>
                    </div>
                ) : null}
                {activeStepName === facilityClaimStepsNames.ADDITIONAL_DATA ? (
                    <div>
                        <Typography variant="display3" style={infoTitleStyle}>
                            Additional Data
                        </Typography>
                        <Typography variant="subheading" style={infoDescStyle}>
                            Use the form below to upload additional information
                            about this production location.
                        </Typography>
                    </div>
                ) : null}
                <Paper style={claimFacilityStepperStyles.paperStyles}>
                    <ActiveStepComponent />
                </Paper>
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
        yourName: string.isRequired,
        yourTitle: string.isRequired,
        agreement: string.isRequired,
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
)(withTheme()(withStyles(stepperStyles)(ClaimFacilityStepper)));
