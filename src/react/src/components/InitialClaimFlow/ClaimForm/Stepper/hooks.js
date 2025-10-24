import { useCallback } from 'react';
import { isStepComplete } from '../utils';

const useStepNavigation = (activeStep, completedSteps, setActiveStep) =>
    useCallback(
        stepIndex => {
            // Only allow navigation to completed steps.
            if (
                isStepComplete(stepIndex, completedSteps) &&
                stepIndex !== activeStep
            ) {
                setActiveStep(stepIndex);
            }
        },
        [activeStep, completedSteps, setActiveStep],
    );

export default useStepNavigation;
