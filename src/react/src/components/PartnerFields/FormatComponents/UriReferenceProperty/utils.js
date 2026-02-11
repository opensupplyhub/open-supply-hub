import endsWith from 'lodash/endsWith';

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
    const stringValue = propertyValue ? String(propertyValue) : '';
    return title ? `${title}: ${stringValue}` : stringValue;
};

export const getDescription = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.description || null;
};

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
