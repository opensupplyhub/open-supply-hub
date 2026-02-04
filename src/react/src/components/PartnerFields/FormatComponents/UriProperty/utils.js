import { getLinkTextFromSchema } from '../../utils';

export const getLinkText = (propertyKey, value, schemaProperties) =>
    getLinkTextFromSchema(propertyKey, value, schemaProperties);

export const getPropertyValue = (propertyKey, value) => value[propertyKey];
