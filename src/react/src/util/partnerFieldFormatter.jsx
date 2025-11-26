import React from 'react';

const ITEM_STYLE = Object.freeze({
    marginBottom: '8px',
});

/**
 * Format constants for JSON Schema
 * Can be extended in the future for other format types (e.g., 'uri-reference', 'email', etc.)
 */
const FORMAT_TYPES = Object.freeze({
    URI: 'uri',
});

/**
 * Extracts properties with specific format from JSON schema
 */
const extractPropertiesByFormat = (schemaProperties, formatType) => {
    const fields = new Set();
    Object.keys(schemaProperties).forEach(propName => {
        const propSchema = schemaProperties[propName];
        if (propSchema?.format === formatType) {
            fields.add(propName);
        }
    });
    return fields;
};

/**
 * Formats a property value with optional label from schema
 */
const formatValueWithLabel = (title, value) => {
    const stringValue = String(value || '');
    return title ? `${title}: ${stringValue}` : stringValue;
};

/**
 * Renders a property value as a div element
 */
const renderPropertyDiv = (key, propValue, displayText) => (
    <div key={`${key}-${propValue}`} style={ITEM_STYLE}>
        {displayText}
    </div>
);

/**
 * Formats an object value, displaying property values with optional labels from schema
 */
const formatPlainObjectValue = (value, schemaProperties = {}) =>
    Object.keys(value).map(key => {
        const propValue = value[key];
        const propSchema = schemaProperties[key] || {};
        const { title } = propSchema;
        const displayText = formatValueWithLabel(title, propValue);

        return renderPropertyDiv(key, propValue, displayText);
    });

/**
 * Renders a URI property as a clickable link
 */
const renderUriLink = (key, uriValue, linkText) => (
    <div key={`${key}-uri-${uriValue}`} style={ITEM_STYLE}>
        <a href={uriValue} target="_blank" rel="noopener noreferrer">
            {linkText}
        </a>
    </div>
);

/**
 * Checks if a key is a text property for a URI field
 */
const isUriTextProperty = (key, uriFields) =>
    key.endsWith('_text') && uriFields.has(key.slice(0, -5));

/**
 * Gets the display text for a URI property, checking for _text sibling
 */
const getUriLinkText = (key, uriValue, value) => {
    const textKey = `${key}_text`;
    return value[textKey] || uriValue;
};

/**
 * Formats an object value with URI fields rendered as clickable links
 */
const formatObjectWithLinks = (value, uriFields, schemaProperties = {}) =>
    Object.keys(value)
        .map(key => {
            const propValue = value[key];

            if (isUriTextProperty(key, uriFields)) {
                return null;
            }

            if (uriFields.has(key)) {
                if (propValue) {
                    const linkText = getUriLinkText(key, propValue, value);
                    return renderUriLink(key, propValue, linkText);
                }
                return null;
            }

            const propSchema = schemaProperties[key] || {};
            const { title } = propSchema;
            const displayText = formatValueWithLabel(title, propValue);

            return renderPropertyDiv(key, propValue, displayText);
        })
        .filter(Boolean);

/**
 * Formats partner field values based on JSON schema.
 */
const formatPartnerFieldWithSchema = (value, jsonSchema) => {
    if (
        !jsonSchema ||
        !value ||
        typeof value !== 'object' ||
        Array.isArray(value)
    ) {
        return value;
    }

    const schemaProperties = jsonSchema?.properties || {};
    const uriFields = extractPropertiesByFormat(
        schemaProperties,
        FORMAT_TYPES.URI,
    );

    if (uriFields.size === 0) {
        return formatPlainObjectValue(value, schemaProperties);
    }

    return formatObjectWithLinks(value, uriFields, schemaProperties);
};

export default formatPartnerFieldWithSchema;
