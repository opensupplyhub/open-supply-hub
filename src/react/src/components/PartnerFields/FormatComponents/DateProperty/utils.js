import { formatDate } from '../../utils';

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
