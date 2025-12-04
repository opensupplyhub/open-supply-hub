import React from 'react';
import UriProperty from './UriProperty';
import UriReferenceProperty from './UriReferenceProperty';
import DefaultProperty from './DefaultProperty';
import { FORMAT_TYPES, getFormatFromSchema, shouldSkipProperty } from './utils';

/**
 * Format component registry.
 * Maps format types to their component functions.
 */
const FORMAT_COMPONENTS = {
    [FORMAT_TYPES.URI]: UriProperty,
    [FORMAT_TYPES.URI_REFERENCE]: UriReferenceProperty,
    // Add more format components here in the future
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
const renderProperty = (
    propertyKey,
    value,
    schemaProperties,
    baseUrl,
    displayText,
) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    const format = getFormatFromSchema(propertySchema);
    const FormatComponent = getFormatComponent(format);

    return (
        <FormatComponent
            key={propertyKey}
            propertyKey={propertyKey}
            value={value}
            schemaProperties={schemaProperties}
            baseUrl={baseUrl}
            displayText={displayText}
        />
    );
};

/**
 * Component to render partner field values based on JSON schema.
 */
const PartnerFieldSchemaValue = ({
    value,
    jsonSchema,
    baseUrl,
    displayText,
}) => {
    if (
        !jsonSchema ||
        !value ||
        typeof value !== 'object' ||
        Array.isArray(value)
    ) {
        return value ?? null;
    }

    const schemaProperties = jsonSchema?.properties || {};

    const renderedItems = Object.keys(value).reduce((acc, propertyKey) => {
        if (shouldSkipProperty(propertyKey, schemaProperties)) {
            return acc;
        }
        const rendered = renderProperty(
            propertyKey,
            value,
            schemaProperties,
            baseUrl,
            displayText,
        );
        if (rendered) {
            acc.push(rendered);
        }
        return acc;
    }, []);

    return <>{renderedItems}</>;
};

export default PartnerFieldSchemaValue;
