/**
 * Get the property value as string
 */
export const getPropertyValueAsString = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return propertyValue == null ? '' : String(propertyValue);
};

/**
 * Get the title from schema if exists
 */
export const getTitleFromSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.title || null;
};
