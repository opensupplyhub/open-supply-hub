import endsWith from 'lodash/endsWith';
/**
 * Format constants for JSON Schema.
 */
export const FORMAT_TYPES = {
    URI: 'uri',
    URI_REFERENCE: 'uri-reference',
    DATE: 'date',
    DATE_TIME: 'date-time',
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

export const showFieldDefaultDisplayText = (
    schemaProperties,
    propertyValue,
    propertyKey,
) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    const { title } = propertySchema;
    const stringValue = propertyValue == null ? '' : String(propertyValue);
    return title ? `${title}: ${stringValue}` : stringValue;
};

export const constructUrlFromPartnerField = (baseUrl, value = '') => {
    if (endsWith(baseUrl, '/')) return baseUrl + value.trim();
    return `${baseUrl}/${value.trim()}`;
};

export const getLinkTextFromSchema = (propertyKey, value, schemaProperties) => {
    const textKey = `${propertyKey}_text`;
    const textPropertyDefined =
        schemaProperties && Boolean(schemaProperties[textKey]);
    if (textPropertyDefined && textKey in value) {
        return value[textKey];
    }
    return value[propertyKey];
};

/**
 * Format date string to readable format (e.g., "October 28, 2023")
 */
export const formatDate = dateString => {
    if (!dateString) return '';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    } catch (error) {
        return dateString;
    }
};

/**
 * Format date-time string to readable format
 */
export const formatDateTime = dateTimeString => {
    if (!dateTimeString) return '';

    try {
        const date = new Date(dateTimeString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    } catch (error) {
        return dateTimeString;
    }
};

/**
 * Check if a property schema represents a nested object
 */
export const isNestedObject = (propertySchema, propertyValue) =>
    propertySchema?.type === 'object' &&
    propertySchema?.properties &&
    typeof propertyValue === 'object' &&
    propertyValue !== null &&
    !Array.isArray(propertyValue);

/**
 * Get the type from a property schema
 */
export const getTypeFromSchema = propertySchema => propertySchema?.type || null;
