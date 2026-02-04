import {
    constructUrlFromPartnerField,
    showFieldDefaultDisplayText,
    getLinkTextFromSchema,
} from '../../utils';

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
