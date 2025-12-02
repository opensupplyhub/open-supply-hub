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
const UriProperty = ({ propertyKey, value, schemaProperties }) => {
    const propertyValue = value[propertyKey];
    if (!propertyValue) {
        return null;
    }

    const textKey = `${propertyKey}_text`;
    const textPropertyDefined = schemaProperties && schemaProperties[textKey];
    const linkText =
        textPropertyDefined &&
        Object.prototype.hasOwnProperty.call(value, textKey)
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
const DefaultProperty = ({ propertyKey, value, schemaProperties }) => {
    const propertyValue = value[propertyKey];
    const propertySchema = schemaProperties[propertyKey] || {};
    const { title } = propertySchema;
    const stringValue = propertyValue != null ? String(propertyValue) : '';
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
 * Checks if a property key should be skipped.
 */
const shouldSkipProperty = (propertyKey, schemaProperties) => {
    if (!Object.prototype.hasOwnProperty.call(schemaProperties, propertyKey)) {
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
const renderProperty = (propertyKey, value, schemaProperties) => {
    if (!Object.prototype.hasOwnProperty.call(value, propertyKey)) {
        return null;
    }

    const propertySchema = schemaProperties[propertyKey] || {};
    const format = getFormatFromSchema(propertySchema);
    const FormatComponent = getFormatComponent(format);

    return (
        <FormatComponent
            key={propertyKey}
            propertyKey={propertyKey}
            value={value}
            schemaProperties={schemaProperties}
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
        .filter(
            propertyKey => !shouldSkipProperty(propertyKey, schemaProperties),
        )
        .map(propertyKey =>
            renderProperty(propertyKey, value, schemaProperties),
        )
        .filter(Boolean);

    return <>{renderedItems}</>;
};

export default PartnerFieldSchemaValue;
