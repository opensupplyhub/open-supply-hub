export const getPropertyValueAsString = (propertyKey, value) => {
    const propertyValue = value[propertyKey];
    return propertyValue == null ? '' : String(propertyValue);
};

export default getPropertyValueAsString;
