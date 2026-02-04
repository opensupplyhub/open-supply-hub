import endsWith from 'lodash/endsWith';
import getLinkTextFromSchema from '../../utils';

/**
 * Construct URL from partner field base URL and value
 */
const constructUrlFromPartnerField = (baseUrl, value = '') => {
    if (endsWith(baseUrl, '/')) return baseUrl + value.trim();
    return `${baseUrl}/${value.trim()}`;
};

/**
 * Show field default display text with title and value
 */
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

/**
 * Get the property value
 */
export const getPropertyValue = (propertyKey, value) => value[propertyKey];

/**
 * Get the description from schema
 */
export const getDescription = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.description || null;
};

/**
 * Get the link text for the URI reference
 */
export const getLinkText = (propertyKey, value, schemaProperties) =>
    getLinkTextFromSchema(propertyKey, value, schemaProperties);

/**
 * Construct the absolute URI from base URL and property value
 */
export const getAbsoluteURI = (baseUrl, propertyValue) => {
    if (!baseUrl) return undefined;
    return constructUrlFromPartnerField(baseUrl, propertyValue);
};

/**
 * Get the display text for the link
 */
export const getDisplayLinkText = (
    baseUrl,
    displayText,
    linkText,
    absoluteURI,
    schemaProperties,
    propertyValue,
    propertyKey,
) => {
    if (baseUrl) {
        return displayText || linkText || absoluteURI;
    }
    return showFieldDefaultDisplayText(
        schemaProperties,
        propertyValue,
        propertyKey,
    );
};
