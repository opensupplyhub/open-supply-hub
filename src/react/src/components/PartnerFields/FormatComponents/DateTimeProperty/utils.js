/**
 * Format date-time string to readable format
 */
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

/**
 * Get the formatted date-time value from the property
 */
export const getFormattedDateTimeValue = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return formatDateTime(propertyValue);
};

/**
 * Get the title from schema if exists
 */
export const getTitleFromSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.title || null;
};
