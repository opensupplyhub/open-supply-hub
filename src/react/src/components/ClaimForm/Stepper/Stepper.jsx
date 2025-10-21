import React from 'react';
import { func, number, arrayOf, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import StepConnector from '@material-ui/core/StepConnector';
import Typography from '@material-ui/core/Typography';
import Schedule from '@material-ui/icons/Schedule';
import Grid from '@material-ui/core/Grid';

import { STEP_NAMES, STEP_SUBTITLES, STEP_TIME_ESTIMATES } from '../constants';
import stepperStyles from './styles';
import useStepNavigation from './hooks';

const ClaimFormStepper = ({
    classes,
    currentStep,
    completedSteps,
    onStepClick,
}) => {
    const handleStepClick = useStepNavigation(
        currentStep,
        completedSteps,
        onStepClick,
    );

    return (
        <Stepper
            activeStep={currentStep}
            alternativeLabel
            className={classes.stepperRoot}
            connector={
                <StepConnector
                    classes={{
                        root: classes.connectorRoot,
                        line: classes.connectorLine,
                    }}
                />
            }
        >
            {STEP_NAMES.map((label, index) => {
                const isClickable = index < currentStep;
                const isActiveOrCompleted = index <= currentStep;

                return (
                    <Step
                        key={label}
                        classes={{
                            root: classes.stepRoot,
                        }}
                    >
                        <StepLabel
                            onClick={() =>
                                isClickable && handleStepClick(index)
                            }
                            classes={{
                                root: classes.stepLabelRoot,
                                labelContainer: classes.stepLabelContainer,
                                iconContainer: isClickable
                                    ? `${classes.stepIconContainer} ${classes.stepIconContainerClickable}`
                                    : classes.stepIconContainer,
                            }}
                        >
                            <Grid container className={classes.stepContent}>
                                <Typography
                                    variant="body2"
                                    className={classes.stepLabel}
                                >
                                    {label}
                                </Typography>
                                {STEP_SUBTITLES[index] && (
                                    <Typography
                                        variant="caption"
                                        className={classes.stepSubtitle}
                                    >
                                        {STEP_SUBTITLES[index]}
                                    </Typography>
                                )}
                                {STEP_TIME_ESTIMATES[index] && (
                                    <Grid
                                        item
                                        container
                                        className={classes.stepTime}
                                    >
                                        <Grid
                                            item
                                            container
                                            className={
                                                classes.stepTimeIconContainer
                                            }
                                        >
                                            <Schedule
                                                className={
                                                    isActiveOrCompleted
                                                        ? `${classes.stepTimeIconActive} ${classes.stepTimeIcon}`
                                                        : classes.stepTimeIcon
                                                }
                                            />
                                        </Grid>
                                        <Grid item>
                                            <Typography
                                                variant="caption"
                                                className={
                                                    isActiveOrCompleted
                                                        ? `${classes.stepTimeTextActive} ${classes.stepTimeText}`
                                                        : classes.stepTimeText
                                                }
                                            >
                                                {STEP_TIME_ESTIMATES[index]}
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                )}
                            </Grid>
                        </StepLabel>
                    </Step>
                );
            })}
        </Stepper>
    );
};

ClaimFormStepper.propTypes = {
    classes: object.isRequired,
    currentStep: number.isRequired,
    completedSteps: arrayOf(number).isRequired,
    onStepClick: func.isRequired,
};

export default withStyles(stepperStyles)(ClaimFormStepper);
