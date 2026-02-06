const formatDateTime = dateTimeString => {
    if (!dateTimeString) return '';

    const date = new Date(dateTimeString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};

export const getFormattedDateTimeValue = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return formatDateTime(propertyValue);
};

export default getFormattedDateTimeValue;
