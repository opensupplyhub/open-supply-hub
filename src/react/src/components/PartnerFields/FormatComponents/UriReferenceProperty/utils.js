import endsWith from 'lodash/endsWith';
import { getLinkTextFromSchema } from '../../utils';

const constructUrlFromPartnerField = (baseUrl, value = '') => {
    if (endsWith(baseUrl, '/')) return baseUrl + value.trim();
    return `${baseUrl}/${value.trim()}`;
};

const showFieldDefaultDisplayText = (
    schemaProperties,
    propertyValue,
    propertyKey,
) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    const { title } = propertySchema;
    const stringValue = propertyValue == null ? '' : String(propertyValue);
    return title ? `${title}: ${stringValue}` : stringValue;
};

export const getPropertyValue = (propertyKey, value) => value[propertyKey];

export const getDescription = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.description || null;
};

export const getLinkText = (propertyKey, value, schemaProperties) =>
    getLinkTextFromSchema(propertyKey, value, schemaProperties);

export const getAbsoluteUri = (baseUrl, propertyValue) => {
    if (!baseUrl) return undefined;
    return constructUrlFromPartnerField(baseUrl, propertyValue);
};

export const getDisplayLinkText = (
    baseUrl,
    displayText,
    linkText,
    absoluteUri,
    schemaProperties,
    propertyValue,
    propertyKey,
) => {
    if (baseUrl) {
        return displayText || linkText || absoluteUri;
    }
    return showFieldDefaultDisplayText(
        schemaProperties,
        propertyValue,
        propertyKey,
    );
};
