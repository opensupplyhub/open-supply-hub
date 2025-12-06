import React from 'react';
import { showFieldDefaultDisplayText } from './utils';

/**
 * Component for rendering default format properties (no format or unsupported format).
 */
const DefaultProperty = ({ propertyKey, value, schemaProperties }) => {
    const propertyValue = value[propertyKey];
    const displayText = showFieldDefaultDisplayText(
        schemaProperties,
        propertyValue,
        propertyKey,
    );

    return (
        <span key={`${propertyKey}-default`} style={{ display: 'block' }}>
            {displayText}
        </span>
    );
};

export default DefaultProperty;
