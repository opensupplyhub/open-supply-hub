import { formatDateTime } from '../../utils';

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
