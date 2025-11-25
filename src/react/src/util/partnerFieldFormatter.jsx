import React from 'react';

/**
 * Formats an object value, displaying only the property values
 */
const formatPlainObjectValue = value =>
    Object.keys(value).map(key => {
        const propValue = value[key];

        return (
            <div key={`${key}-${propValue}`} style={{ marginBottom: '8px' }}>
                {String(propValue || '')}
            </div>
        );
    });

/**
 * Formats an object value with URI fields rendered as clickable links
 */
const formatObjectWithLinks = (value, uriFields) =>
    Object.keys(value)
        .map(key => {
            const propValue = value[key];

            if (key.endsWith('_text') && uriFields.has(key.slice(0, -5))) {
                return null;
            }

            if (uriFields.has(key)) {
                const uriValue = propValue;
                const textKey = `${key}_text`;
                const linkText = value[textKey] || uriValue;

                if (uriValue) {
                    return (
                        <div
                            key={`${key}-uri-${uriValue}`}
                            style={{ marginBottom: '8px' }}
                        >
                            <a
                                href={uriValue}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {linkText}
                            </a>
                        </div>
                    );
                }
            }

            if (!key.endsWith('_text') || !uriFields.has(key.slice(0, -5))) {
                return (
                    <div
                        key={`${key}-text-${propValue}`}
                        style={{ marginBottom: '8px' }}
                    >
                        {String(propValue || '')}
                    </div>
                );
            }

            return null;
        })
        .filter(Boolean);

/**
 * Formats partner field values based on JSON schema.
 * Renders URI properties (format: "uri") as clickable links.
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
    const uriFields = new Set();

    Object.keys(schemaProperties).forEach(propName => {
        const propSchema = schemaProperties[propName];
        if (propSchema?.format === 'uri') {
            uriFields.add(propName);
        }
    });

    if (uriFields.size === 0) {
        return formatPlainObjectValue(value);
    }

    return formatObjectWithLinks(value, uriFields);
};

export default formatPartnerFieldWithSchema;
