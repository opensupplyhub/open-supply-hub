export const getPropertyValueAsString = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return propertyValue ? String(propertyValue) : '';
};

export default getPropertyValueAsString;
