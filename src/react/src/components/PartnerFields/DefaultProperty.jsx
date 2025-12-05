import React from 'react';
import { getFormatFromSchema } from './utils';

/**
 * Component for rendering default format properties (no format or unsupported format).
 */
const DefaultProperty = ({ propertyKey, value, schemaProperties }) => {
    const propertyValue = value[propertyKey];

    return (
        <span key={`${propertyKey}-default`} style={{ display: 'block' }}>
            {getFormatFromSchema(schemaProperties, propertyValue, propertyKey)}
        </span>
    );
};

export default DefaultProperty;
