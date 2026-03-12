const getSelectedDrawerField = (fields, fieldKey) =>
    fieldKey
        ? (fields && fields.find(field => field.key === fieldKey)) ?? null
        : null;

export default getSelectedDrawerField;
