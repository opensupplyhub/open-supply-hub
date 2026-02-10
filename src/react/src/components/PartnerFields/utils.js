import moment from 'moment';

export const getTitleFromSchema = (propertyKey, schemaProperties) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    return propertySchema.title || null;
};

export const getLinkTextFromSchema = (propertyKey, value, schemaProperties) => {
    const textKey = `${propertyKey}_text`;
    const textPropertyDefined =
        schemaProperties && Boolean(schemaProperties[textKey]);
    if (textPropertyDefined && textKey in value) {
        return value[textKey];
    }
    return value[propertyKey];
};

export const getFormattedDateValue = (propertyKey, value, format = 'LL') => {
    const propertyValue = value[propertyKey];
    if (!propertyValue) return '';
    return moment(propertyValue).format(format);
};
