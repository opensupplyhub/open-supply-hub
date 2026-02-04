export const getNestedValue = (propertyKey, value) => value[propertyKey];

export const createNestedSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return {
        properties: propertySchema.properties || {},
    };
};
