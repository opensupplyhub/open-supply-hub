import { CLAIM_FORM_STEPS, TOTAL_STEPS } from './constants';

/**
 * Check if a step is complete
 * @param {number} stepIndex - The index of the step to check
 * @param {Array} completedSteps - Array of completed step indices
 * @returns {boolean} - Whether the step is complete
 */
export const isStepComplete = (stepIndex, completedSteps) =>
    completedSteps.includes(stepIndex);

/**
 * Check if a step is accessible (clickable)
 * @param {number} stepIndex - The index of the step to check
 * @param {number} activeStep - The current active step index
 * @param {Array} completedSteps - Array of completed step indices
 * @returns {boolean} - Whether the step is accessible
 */
export const isStepAccessible = (stepIndex, activeStep, completedSteps) => {
    // Current step is always accessible
    if (stepIndex === activeStep) return true;

    // Completed steps are accessible
    if (completedSteps.includes(stepIndex)) return true;

    // Step immediately after last completed step is accessible
    if (stepIndex === completedSteps.length) return true;

    return false;
};

/**
 * Get the next step index
 * @param {number} currentStep - The current step index
 * @returns {number} - The next step index
 */
export const getNextStep = currentStep =>
    Math.min(currentStep + 1, TOTAL_STEPS - 1);

/**
 * Get the previous step index
 * @param {number} currentStep - The current step index
 * @returns {number} - The previous step index
 */
export const getPreviousStep = currentStep => Math.max(currentStep - 1, 0);

/**
 * Check if the current step is the first step
 * @param {number} stepIndex - The step index to check
 * @returns {boolean} - Whether it's the first step
 */
export const isFirstStep = stepIndex =>
    stepIndex === CLAIM_FORM_STEPS.ELIGIBILITY;

/**
 * Check if the current step is the last step
 * @param {number} stepIndex - The step index to check
 * @returns {boolean} - Whether it's the last step
 */
export const isLastStep = stepIndex => stepIndex === CLAIM_FORM_STEPS.PROFILE;

/**
 * Check if all required steps are completed
 * @param {Array} completedSteps - Array of completed step indices
 * @returns {boolean} - Whether all steps are complete
 */
export const areAllStepsComplete = completedSteps =>
    completedSteps.length === TOTAL_STEPS;
