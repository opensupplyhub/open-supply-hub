/**
 * Get the nested value from the property
 */
export const getNestedValue = (propertyKey, value) => value[propertyKey];

/**
 * Get the title from schema if exists
 */
export const getTitleFromSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.title || null;
};

/**
 * Create nested schema for recursive rendering
 */
export const createNestedSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return {
        properties: propertySchema.properties || {},
    };
};
