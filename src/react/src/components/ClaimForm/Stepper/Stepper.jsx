import React from 'react';
import { func, number, arrayOf } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import StepConnector from '@material-ui/core/StepConnector';
import Typography from '@material-ui/core/Typography';
import Security from '@material-ui/icons/Security';
import People from '@material-ui/icons/People';
import Language from '@material-ui/icons/Language';
import Business from '@material-ui/icons/Business';
import Schedule from '@material-ui/icons/Schedule';

import {
    STEP_NAMES,
    STEP_SUBTITLES,
    STEP_TIME_ESTIMATES,
    STEP_ICONS,
} from '../constants';
import stepperStyles from './styles';
import useStepNavigation from './hooks';

const iconComponents = {
    Security,
    People,
    Language,
    Business,
};

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

    const getStepIcon = stepIndex => {
        const iconName = STEP_ICONS[stepIndex];
        const IconComponent = iconComponents[iconName] || Business;
        const isCompleted = completedSteps.includes(stepIndex);
        const isActiveStep = stepIndex === currentStep;

        return (
            <IconComponent
                className={
                    isActiveStep || isCompleted
                        ? classes.stepIconActive
                        : classes.stepIcon
                }
            />
        );
    };

    return (
        <Stepper
            activeStep={currentStep}
            alternativeLabel
            className={classes.stepperRoot}
            connector={
                <StepConnector
                    classes={{
                        active: classes.connectorActive,
                        completed: classes.connectorCompleted,
                        line: classes.connectorLine,
                    }}
                />
            }
        >
            {STEP_NAMES.map((label, index) => {
                const isClickable = completedSteps.includes(index);

                return (
                    <Step
                        key={label}
                        completed={completedSteps.includes(index)}
                    >
                        <StepLabel
                            icon={getStepIcon(index)}
                            classes={{
                                root: classes.stepLabel,
                                active: classes.stepLabelActive,
                                completed: classes.stepLabelCompleted,
                            }}
                            onClick={() =>
                                isClickable && handleStepClick(index)
                            }
                            style={{
                                cursor: isClickable ? 'pointer' : 'default',
                            }}
                        >
                            <div className={classes.stepContent}>
                                <Typography variant="body2">{label}</Typography>
                                {STEP_SUBTITLES[index] && (
                                    <Typography
                                        variant="caption"
                                        className={classes.stepSubtitle}
                                    >
                                        {STEP_SUBTITLES[index]}
                                    </Typography>
                                )}
                                {STEP_TIME_ESTIMATES[index] && (
                                    <div className={classes.stepTime}>
                                        <Schedule
                                            style={{
                                                fontSize: '0.875rem',
                                            }}
                                        />
                                        <Typography variant="caption">
                                            {STEP_TIME_ESTIMATES[index]}
                                        </Typography>
                                    </div>
                                )}
                            </div>
                        </StepLabel>
                    </Step>
                );
            })}
        </Stepper>
    );
};

ClaimFormStepper.propTypes = {
    classes: func.isRequired,
    currentStep: number.isRequired,
    completedSteps: arrayOf(number).isRequired,
    onStepClick: func.isRequired,
};

export default withStyles(stepperStyles)(ClaimFormStepper);
