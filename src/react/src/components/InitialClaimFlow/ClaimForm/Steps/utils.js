/**
 * Finds and returns the option object whose label matches the selectedLabel.
 * Helps convert the value to an object that can be supported by the
 * StyledSelect component.
 */
const findSelectedOption = (options, selectedLabel) => {
    if (!selectedLabel) return null;
    return options.find(opt => opt.label === selectedLabel) || null;
};

export default findSelectedOption;
