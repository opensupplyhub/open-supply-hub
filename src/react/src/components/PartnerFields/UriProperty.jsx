import React from 'react';
import { getLinkTextFromSchema } from './utils';

/**
 * Component for rendering URI format properties.
 */
const UriProperty = ({ propertyKey, value, schemaProperties }) => {
    const propertyValue = value[propertyKey];
    if (!propertyValue) {
        return null;
    }

    const linkText = getLinkTextFromSchema(
        propertyKey,
        value,
        schemaProperties,
    );

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
