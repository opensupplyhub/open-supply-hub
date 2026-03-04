const getAriaLabelFromTitle = title =>
    typeof title === 'string' ? title : undefined;

export default getAriaLabelFromTitle;
