import getLinkTextFromSchema from '../../utils';

/**
 * Get the link text for URI property
 */
export const getLinkText = (propertyKey, value, schemaProperties) =>
    getLinkTextFromSchema(propertyKey, value, schemaProperties);

/**
 * Get the title from schema if exists
 */
export const getTitleFromSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.title || null;
};

/**
 * Get the property value
 */
export const getPropertyValue = (propertyKey, value) => value[propertyKey];
