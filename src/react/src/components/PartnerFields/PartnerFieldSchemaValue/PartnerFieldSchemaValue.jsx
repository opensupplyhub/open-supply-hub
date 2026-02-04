import React from 'react';
import { oneOfType, object, string, number, bool, shape } from 'prop-types';
import {
    isValidValue,
    getSchemaProperties,
    renderProperties,
} from './utils.jsx';

const PartnerFieldSchemaValue = ({
    value,
    jsonSchema,
    partnerConfigFields,
}) => {
    if (!isValidValue(value, jsonSchema)) {
        return null;
    }

    const schemaProperties = getSchemaProperties(jsonSchema);

    const renderedItems = renderProperties(
        value,
        schemaProperties,
        partnerConfigFields,
    );

    return <>{renderedItems}</>;
};

PartnerFieldSchemaValue.propTypes = {
    value: oneOfType([object, string, number, bool]).isRequired,
    jsonSchema: shape({
        properties: object,
    }),
    partnerConfigFields: shape({
        baseUrl: string,
        displayText: string,
    }),
};

PartnerFieldSchemaValue.defaultProps = {
    jsonSchema: null,
    partnerConfigFields: null,
};

export default PartnerFieldSchemaValue;
