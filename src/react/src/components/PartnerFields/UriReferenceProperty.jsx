/* eslint no-unused-vars: 0 */
import React from 'react';
import { constructUrlFromPartnerField } from './utils.js';

/**
 * Component for rendering URI-reference format properties.
 */
const UriReferenceProperty = ({
    propertyKey,
    value,
    schemaProperties,
    baseUrl,
    displayText,
}) => {
    const propertyValue = value[propertyKey];
    if (!propertyValue) {
        return null;
    }

    const textKey = `${propertyKey}_text`;
    const textPropertyDefined = schemaProperties && schemaProperties[textKey];

    const {
        value: { description },
    } = schemaProperties;

    const linkText =
        textPropertyDefined && textKey in value
            ? value[textKey]
            : propertyValue;
    const absoluteURI = constructUrlFromPartnerField(baseUrl, linkText);

    return (
        <>
            {description ? <p>{description}</p> : null}
            <a
                key={`${propertyKey}-uri-${propertyValue}`}
                href={absoluteURI}
                target="_blank"
                rel="noopener noreferrer"
            >
                {displayText ? <p>{displayText}</p> : null}
            </a>
        </>
    );
};

export default UriReferenceProperty;
