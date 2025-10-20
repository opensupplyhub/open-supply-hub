import { useCallback } from 'react';

/**
 * Hook to handle step navigation
 * @param {number} activeStep - Current active step
 * @param {Array} completedSteps - Array of completed step indices
 * @param {Function} setActiveStep - Function to set active step
 * @returns {Function} - Step click handler
 */
const useStepNavigation = (activeStep, completedSteps, setActiveStep) =>
    useCallback(
        stepIndex => {
            // Only allow navigation to completed steps
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
