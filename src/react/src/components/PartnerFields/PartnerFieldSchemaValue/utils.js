import {
    FORMAT_TYPES,
    FORMAT_COMPONENTS,
    TYPE_COMPONENTS,
    DEFAULT_COMPONENT,
} from './constants';

/**
 * Gets the format type from a property schema.
 */
const getFormatFromSchema = propertySchema => propertySchema?.format || null;

/**
 * Checks if a property key should be skipped.
 */
const shouldSkipProperty = (propertyKey, schemaProperties) => {
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

/**
 * Check if a property schema represents a nested object
 */
const isNestedObject = (propertySchema, propertyValue) =>
    propertySchema?.type === 'object' &&
    propertySchema?.properties &&
    typeof propertyValue === 'object' &&
    propertyValue !== null &&
    !Array.isArray(propertyValue);

/**
 * Get the type from a property schema
 */
const getTypeFromSchema = propertySchema => propertySchema?.type || null;

/**
 * Gets the component based on format, then type, then default.
 */
export const getComponentForProperty = (propertySchema, propertyValue) => {
    const format = getFormatFromSchema(propertySchema);
    if (format && FORMAT_COMPONENTS[format]) {
        return FORMAT_COMPONENTS[format];
    }

    if (isNestedObject(propertySchema, propertyValue)) {
        return TYPE_COMPONENTS.object;
    }

    const type = getTypeFromSchema(propertySchema);
    if (type && TYPE_COMPONENTS[type]) {
        return TYPE_COMPONENTS[type];
    }

    return DEFAULT_COMPONENT;
};

/**
 * Check if value is valid for rendering
 */
export const isValidValue = (value, jsonSchema) => {
    if (!jsonSchema || !value) {
        return false;
    }
    if (typeof value !== 'object' || Array.isArray(value)) {
        return false;
    }
    return true;
};

/**
 * Get schema properties from jsonSchema
 */
export const getSchemaProperties = jsonSchema => jsonSchema?.properties || {};

/**
 * Get root title from jsonSchema
 */
export const getRootTitle = jsonSchema => jsonSchema?.title || null;

/**
 * Check if this is a flat schema (no nested objects)
 */
export const isFlatSchema = schemaProperties =>
    Object.keys(schemaProperties).every(key => {
        const propSchema = schemaProperties[key];
        return propSchema?.type !== 'object' || !propSchema?.properties;
    });

/**
 * Render properties from value object
 */
export const renderProperties = (
    value,
    schemaProperties,
    partnerConfigFields,
    renderProperty,
) =>
    Object.keys(value).reduce((acc, propertyKey) => {
        if (shouldSkipProperty(propertyKey, schemaProperties)) {
            return acc;
        }
        const rendered = renderProperty(
            propertyKey,
            value,
            schemaProperties,
            partnerConfigFields,
        );
        if (rendered) {
            acc.push(rendered);
        }
        return acc;
    }, []);
