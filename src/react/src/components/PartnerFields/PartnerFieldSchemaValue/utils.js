import {
    FORMAT_TYPES,
    getFormatFromSchema,
    shouldSkipProperty,
    isNestedObject,
    getTypeFromSchema,
} from '../utils';
import UriProperty from '../FormatComponents/UriProperty/UriProperty';
import UriReferenceProperty from '../FormatComponents/UriReferenceProperty/UriReferenceProperty';
import DateProperty from '../FormatComponents/DateProperty/DateProperty';
import DateTimeProperty from '../FormatComponents/DateTimeProperty/DateTimeProperty';
import IntegerProperty from '../TypeComponents/IntegerProperty/IntegerProperty';
import NestedObjectProperty from '../TypeComponents/NestedObjectProperty/NestedObjectProperty';
import DefaultProperty from '../TypeComponents/DefaultProperty/DefaultProperty';

/**
 * Format component registry.
 * Maps format types to their component functions.
 */
const FORMAT_COMPONENTS = {
    [FORMAT_TYPES.URI]: UriProperty,
    [FORMAT_TYPES.URI_REFERENCE]: UriReferenceProperty,
    [FORMAT_TYPES.DATE]: DateProperty,
    [FORMAT_TYPES.DATE_TIME]: DateTimeProperty,
};

/**
 * Type component registry.
 * Maps schema types to their component functions.
 */
const TYPE_COMPONENTS = {
    integer: IntegerProperty,
    object: NestedObjectProperty,
};

/**
 * Gets the component based on format, then type, then default.
 */
export const getComponentForProperty = (propertySchema, propertyValue) => {
    const format = getFormatFromSchema(propertySchema);
    if (format && FORMAT_COMPONENTS[format]) {
        return FORMAT_COMPONENTS[format];
    }

    if (isNestedObject(propertySchema, propertyValue)) {
        return NestedObjectProperty;
    }

    const type = getTypeFromSchema(propertySchema);
    if (type && TYPE_COMPONENTS[type]) {
        return TYPE_COMPONENTS[type];
    }

    return DefaultProperty;
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
