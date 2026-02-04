import React from 'react';
import { oneOfType, object, string, number, bool, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import {
    getComponentForProperty,
    isValidValue,
    getSchemaProperties,
    getRootTitle,
    isFlatSchema,
    renderProperties,
} from './utils';
import partnerFieldSchemaValueStyles from './styles';

/**
 * Renders a single property based on format/type strategy.
 */
const renderProperty = (
    propertyKey,
    value,
    schemaProperties,
    partnerConfigFields,
) => {
    const propertySchema = schemaProperties[propertyKey] || {};
    const propertyValue = value[propertyKey];
    const Component = getComponentForProperty(propertySchema, propertyValue);

    return (
        <Component
            key={propertyKey}
            propertyKey={propertyKey}
            value={value}
            schemaProperties={schemaProperties}
            partnerConfigFields={partnerConfigFields}
        />
    );
};

/**
 * Component to render partner field values based on JSON schema.
 */
const PartnerFieldSchemaValue = ({
    value,
    jsonSchema,
    partnerConfigFields,
    classes,
}) => {
    if (!isValidValue(value, jsonSchema)) {
        return value ?? null;
    }

    const schemaProperties = getSchemaProperties(jsonSchema);
    const rootTitle = getRootTitle(jsonSchema);

    console.log('jsonSchema', jsonSchema);
    console.log('value', value);
    console.log('partnerConfigFields', partnerConfigFields);

    const renderedItems = renderProperties(
        value,
        schemaProperties,
        partnerConfigFields,
        renderProperty,
    );

    // If flat schema and has root title, display it
    if (isFlatSchema(schemaProperties) && rootTitle) {
        return (
            <>
                <div className={classes.rootTitle}>{rootTitle}</div>
                {renderedItems}
            </>
        );
    }

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
    classes: object.isRequired,
};

PartnerFieldSchemaValue.defaultProps = {
    jsonSchema: null,
    partnerConfigFields: null,
};

export default withStyles(partnerFieldSchemaValueStyles)(
    PartnerFieldSchemaValue,
);
