import { useCallback } from 'react';

const useStepNavigation = (activeStep, completedSteps, setActiveStep) =>
    useCallback(
        stepIndex => {
            // Only allow navigation to completed steps.
            if (
                completedSteps.includes(stepIndex) &&
                stepIndex !== activeStep
            ) {
                setActiveStep(stepIndex);
            }
        },
        [activeStep, completedSteps, setActiveStep],
    );

export default useStepNavigation;
