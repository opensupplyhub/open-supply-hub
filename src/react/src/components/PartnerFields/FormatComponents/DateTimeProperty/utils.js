const formatDateTime = dateTimeString => {
    if (!dateTimeString) return '';

    try {
        const date = new Date(dateTimeString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    } catch (error) {
        return dateTimeString;
    }
};

export const getFormattedDateTimeValue = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return formatDateTime(propertyValue);
};

export default getFormattedDateTimeValue;
