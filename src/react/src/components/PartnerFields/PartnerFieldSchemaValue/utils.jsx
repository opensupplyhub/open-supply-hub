import React from 'react';
import {
    FORMAT_TYPES,
    FORMAT_COMPONENTS,
    TYPE_COMPONENTS,
    DEFAULT_COMPONENT,
} from './constants';

const getFormatFromSchema = propertySchema => propertySchema?.format || null;

const getTypeFromSchema = propertySchema => propertySchema?.type || null;

const shouldSkipProperty = (propertyKey, schemaProperties) => {
    if (!(propertyKey in schemaProperties)) {
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

const isNestedObject = (propertySchema, propertyValue) =>
    propertySchema?.type === 'object' &&
    propertySchema?.properties &&
    typeof propertyValue === 'object' &&
    propertyValue !== null &&
    !Array.isArray(propertyValue);

export const getComponentForProperty = (propertySchema, propertyValue) => {
    const format = getFormatFromSchema(propertySchema);
    if (format && FORMAT_COMPONENTS[format]) {
        return FORMAT_COMPONENTS[format];
    }

    if (isNestedObject(propertySchema, propertyValue)) {
        return TYPE_COMPONENTS.object;
    }

    const type = getTypeFromSchema(propertySchema);
    if (type && TYPE_COMPONENTS[type]) {
        return TYPE_COMPONENTS[type];
    }

    return DEFAULT_COMPONENT;
};

export const isValidValue = (value, jsonSchema) => {
    if (!jsonSchema || !value) {
        return false;
    }
    if (typeof value !== 'object' || Array.isArray(value)) {
        return false;
    }
    return true;
};

export const getSchemaProperties = jsonSchema => jsonSchema?.properties || {};

export const renderProperty = (
    propertyKey,
    value,
    schemaProperties,
    partnerConfigFields,
) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    const propertyValue = value[propertyKey];
    const Component = getComponentForProperty(propertySchema, propertyValue);

    return (
        <Component
            key={propertyKey}
            propertyKey={propertyKey}
            value={value}
            schemaProperties={schemaProperties}
            partnerConfigFields={partnerConfigFields}
        />
    );
};

export const renderProperties = (
    value,
    schemaProperties,
    partnerConfigFields,
) =>
    Object.keys(value).reduce((acc, propertyKey) => {
        if (shouldSkipProperty(propertyKey, schemaProperties)) {
            return acc;
        }
        const rendered = renderProperty(
            propertyKey,
            value,
            schemaProperties,
            partnerConfigFields,
        );
        if (rendered) {
            acc.push(rendered);
        }
        return acc;
    }, []);
