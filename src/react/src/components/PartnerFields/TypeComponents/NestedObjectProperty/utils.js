const createNestedSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return {
        properties: propertySchema.properties || {},
    };
};

export default createNestedSchema;
