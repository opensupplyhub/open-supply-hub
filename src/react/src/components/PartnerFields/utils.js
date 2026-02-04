/**
 * Gets the link text from schema, checking for a companion _text property.
 * Used by UriProperty and UriReferenceProperty components.
 */
export const getLinkTextFromSchema = (propertyKey, value, schemaProperties) => {
    const textKey = `${propertyKey}_text`;
    const textPropertyDefined =
        schemaProperties && Boolean(schemaProperties[textKey]);
    if (textPropertyDefined && textKey in value) {
        return value[textKey];
    }
    return value[propertyKey];
};

export default getLinkTextFromSchema;
