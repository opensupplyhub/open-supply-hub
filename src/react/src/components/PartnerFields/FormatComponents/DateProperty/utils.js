const formatDate = dateString => {
    if (!dateString) return '';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
};

export const getFormattedDateValue = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return formatDate(propertyValue);
};

export default getFormattedDateValue;
