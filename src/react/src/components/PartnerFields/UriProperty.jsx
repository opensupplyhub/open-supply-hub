import React from 'react';

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
        textPropertyDefined && textKey in value
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

export default UriProperty;
