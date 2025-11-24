import React from 'react';

/**
 * Component for rendering URI format properties.
 */
const UriReferenceProperty = ({ propertyKey, value, schemaProperties }) => {
    const propertyValue = value[propertyKey];
    console.log('propertyValue: ', propertyValue);
    console.log('schemaProperties in UriReferenceProperty: ', schemaProperties);
    if (!propertyValue) {
        return null;
    }

    const textKey = `${propertyKey}_text`;
    const textPropertyDefined = schemaProperties && schemaProperties[textKey];

    console.log('textKey: ', textKey);

    const linkText =
        textPropertyDefined && textKey in value
            ? value[textKey]
            : propertyValue;

    console.log('Link text: ', linkText);

    const {
        value: { description },
    } = schemaProperties;

    console.log(description);

    if (description) {
        console.log(description);
    }

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

export default UriReferenceProperty;
