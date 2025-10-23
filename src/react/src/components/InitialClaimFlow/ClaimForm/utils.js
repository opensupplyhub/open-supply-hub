import { CLAIM_FORM_STEPS, TOTAL_STEPS } from './constants';

export const isStepComplete = (stepIndex, completedSteps) =>
    completedSteps.includes(stepIndex);

export const isStepAccessible = (stepIndex, activeStep, completedSteps) => {
    // Current step is always accessible.
    if (stepIndex === activeStep) return true;

    // Completed steps are accessible.
    if (completedSteps.includes(stepIndex)) return true;

    // Step immediately after last completed step is accessible.
    if (stepIndex === completedSteps.length) return true;

    return false;
};

export const getNextStep = currentStep =>
    Math.min(currentStep + 1, TOTAL_STEPS - 1);

export const getPreviousStep = currentStep => Math.max(currentStep - 1, 0);

export const isFirstStep = stepIndex =>
    stepIndex === CLAIM_FORM_STEPS.ELIGIBILITY;

export const isLastStep = stepIndex => stepIndex === CLAIM_FORM_STEPS.PROFILE;

export const areAllStepsComplete = completedSteps =>
    completedSteps.length === TOTAL_STEPS;
