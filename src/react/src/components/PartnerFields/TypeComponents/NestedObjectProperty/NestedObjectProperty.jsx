import React from 'react';
import { string, object, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import PartnerFieldSchemaValue from '../../PartnerFieldSchemaValue/PartnerFieldSchemaValue';
import {
    getNestedValue,
    getTitleFromSchema,
    createNestedSchema,
} from './utils';
import nestedObjectPropertyStyles from './styles';

/**
 * Component for rendering nested object properties.
 * Recursively renders nested properties using PartnerFieldSchemaValue.
 */
const NestedObjectProperty = ({
    propertyKey,
    value,
    schemaProperties,
    partnerConfigFields,
    classes,
}) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const nestedValue = getNestedValue(propertyKey, value);
    const nestedSchema = createNestedSchema(propertyKey, schemaProperties);

    // If no title, render nested content without header
    if (!title) {
        return (
            <div className={classes.container}>
                <PartnerFieldSchemaValue
                    value={nestedValue}
                    jsonSchema={nestedSchema}
                    partnerConfigFields={partnerConfigFields}
                />
            </div>
        );
    }

    return (
        <div className={classes.container}>
            <div className={classes.title}>{title}</div>
            <div className={classes.content}>
                <PartnerFieldSchemaValue
                    value={nestedValue}
                    jsonSchema={nestedSchema}
                    partnerConfigFields={partnerConfigFields}
                />
            </div>
        </div>
    );
};

NestedObjectProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    partnerConfigFields: shape({
        baseUrl: string,
        displayText: string,
    }),
    classes: object.isRequired,
};

NestedObjectProperty.defaultProps = {
    partnerConfigFields: null,
};

export default withStyles(nestedObjectPropertyStyles)(NestedObjectProperty);
