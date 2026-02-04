/**
 * Format date string to readable format (e.g., "October 28, 2023")
 */
const formatDate = dateString => {
    if (!dateString) return '';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    } catch (error) {
        return dateString;
    }
};

/**
 * Get the formatted date value from the property
 */
export const getFormattedDateValue = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return formatDate(propertyValue);
};

/**
 * Get the title from schema if exists
 */
export const getTitleFromSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.title || null;
};
