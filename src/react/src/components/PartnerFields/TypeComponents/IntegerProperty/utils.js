/**
 * Get the property value
 */
export const getPropertyValue = (propertyKey, value) => value[propertyKey];

/**
 * Get the title from schema if exists
 */
export const getTitleFromSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.title || null;
};
