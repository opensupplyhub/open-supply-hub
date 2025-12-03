import React from 'react';

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

export default DefaultProperty;
