/**
 * Format constants for JSON Schema.
 */
export const FORMAT_TYPES = {
    URI: 'uri',
};

/**
 * Gets the format type from a property schema.
 */
export const getFormatFromSchema = propertySchema =>
    propertySchema?.format || null;

/**
 * Checks if a property key should be skipped.
 */
export const shouldSkipProperty = (propertyKey, schemaProperties) => {
    if (!(propertyKey in schemaProperties)) {
        return true;
    }

    if (propertyKey.endsWith('_text')) {
        const baseKey = propertyKey.slice(0, -5);
        const baseSchema = schemaProperties[baseKey];
        const baseFormat = getFormatFromSchema(baseSchema);

        if (baseFormat === FORMAT_TYPES.URI) {
            return true;
        }
    }

    return false;
};
