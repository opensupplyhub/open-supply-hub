/**
 * Finds and returns the option object whose label matches the selectedLabel.
 * Helps convert the value to an object that can be supported by the
 * StyledSelect component.
 */
const findSelectedOption = (options, selectedLabel) => {
    if (!selectedLabel) return null;
    return options.find(opt => opt.label === selectedLabel) || null;
};

/**
 * Text shown for an option in a verification dropdown. An option can carry
 * a `note` (e.g. "(can delay approval)") that is shown after its label.
 * The note is display only: the option's `label` is what the claim stores,
 * so it must never be folded into `label` itself.
 */
export const getOptionLabelWithNote = option =>
    option.note ? `${option.label} ${option.note}` : option.label;

export default findSelectedOption;
