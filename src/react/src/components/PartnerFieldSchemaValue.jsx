import React from 'react';

/**
 * Format constants for JSON Schema.
 */
const FORMAT_TYPES = Object.freeze({
    URI: 'uri',
});

/**
 * Component for rendering URI format properties.
 */
const UriProperty = ({ propertyKey, propertyValue, value }) => {
    if (!propertyValue) {
        return null;
    }

    const textKey = `${propertyKey}_text`;
    const linkText = Object.prototype.hasOwnProperty.call(value, textKey)
        ? value[textKey]
        : propertyValue;

    return (
        <a
            key={`${propertyKey}-uri-${propertyValue}`}
            href={propertyValue}
            target="_blank"
            rel="noopener noreferrer"
        >
            {linkText}
        </a>
    );
};

/**
 * Component for rendering default format properties (no format or unsupported format).
 */
const DefaultProperty = ({ propertyKey, propertyValue, propertySchema }) => {
    const { title } = propertySchema || {};
    const stringValue = String(propertyValue || '');
    const displayText = title ? `${title}: ${stringValue}` : stringValue;

    return (
        <span key={`${propertyKey}-default`} style={{ display: 'block' }}>
            {displayText}
        </span>
    );
};

/**
 * Format component registry.
 * Maps format types to their component functions.
 */
const FORMAT_COMPONENTS = Object.freeze({
    [FORMAT_TYPES.URI]: UriProperty,
    // Add more format components here in the future
});

/**
 * Gets the format type from a property schema.
 */
const getFormatFromSchema = propertySchema => propertySchema?.format || null;

/**
 * Checks if a property key should be skipped (e.g., _text properties for URI fields).
 */
const shouldSkipProperty = (propertyKey, propertySchema, schemaProperties) => {
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
 * Gets the component to use for rendering a property based on its format.
 */
const getFormatComponent = format => {
    if (format && FORMAT_COMPONENTS[format]) {
        return FORMAT_COMPONENTS[format];
    }
    return DefaultProperty;
};

/**
 * Renders a single property based on format strategy.
 */
const renderProperty = (propertyKey, propertyValue, propertySchema, value) => {
    const format = getFormatFromSchema(propertySchema);

    if (!Object.prototype.hasOwnProperty.call(value, propertyKey)) {
        return null;
    }

    const FormatComponent = getFormatComponent(format);

    return (
        <FormatComponent
            key={propertyKey}
            propertyKey={propertyKey}
            propertyValue={propertyValue}
            propertySchema={propertySchema}
            value={value}
        />
    );
};

/**
 * Component to render partner field values based on JSON schema.
 */
const PartnerFieldSchemaValue = ({ value, jsonSchema }) => {
    if (
        !jsonSchema ||
        !value ||
        typeof value !== 'object' ||
        Array.isArray(value)
    ) {
        return value;
    }

    const schemaProperties = jsonSchema?.properties || {};

    const renderedItems = Object.keys(value)
        .filter(propertyKey => {
            const propertySchema = schemaProperties[propertyKey] || {};
            return !shouldSkipProperty(
                propertyKey,
                propertySchema,
                schemaProperties,
            );
        })
        .map(propertyKey => {
            const propertyValue = value[propertyKey];
            const propertySchema = schemaProperties[propertyKey] || {};
            return renderProperty(
                propertyKey,
                propertyValue,
                propertySchema,
                value,
            );
        })
        .filter(Boolean);

    return <>{renderedItems}</>;
};

export default PartnerFieldSchemaValue;
