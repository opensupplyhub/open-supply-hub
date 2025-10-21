/**
 * Get the appropriate icon component for a step
 * @param {string} iconName - Name of the icon
 * @returns {string} - Icon name that maps to Material-UI icon
 */
export const getStepIcon = iconName => iconName;

/**
 * Determine if a step should be clickable
 * @param {number} stepIndex - Index of the step
 * @param {number} activeStep - Current active step
 * @param {Array} completedSteps - Array of completed step indices
 * @returns {boolean} - Whether the step is clickable
 */
export const isStepClickable = (stepIndex, activeStep, completedSteps) => {
    // Current step is not clickable (already there)
    if (stepIndex === activeStep) return false;

    // Completed steps are clickable
    return completedSteps.includes(stepIndex);
};

/**
 * Get step label classes based on state
 * @param {number} stepIndex - Index of the step
 * @param {number} activeStep - Current active step
 * @param {Array} completedSteps - Array of completed step indices
 * @param {Object} classes - Material-UI classes object
 * @returns {Object} - Classes to apply
 */
export const getStepLabelClasses = (
    stepIndex,
    activeStep,
    completedSteps,
    classes,
) => {
    const isActive = stepIndex === activeStep;
    const isCompleted = completedSteps.includes(stepIndex);

    return {
        root: classes.stepLabel,
        active: isActive ? classes.stepLabelActive : undefined,
        completed: isCompleted ? classes.stepLabelCompleted : undefined,
    };
};

