import React from 'react';
import { string, object, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema } from '../../utils';
import PartnerFieldSchemaValue from '../../PartnerFieldSchemaValue/PartnerFieldSchemaValue';
import createNestedSchema from './utils';
import nestedObjectPropertyStyles from './styles';

const NestedObjectProperty = ({
    propertyKey,
    value,
    schemaProperties,
    partnerConfigFields,
    classes,
}) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const displayPropertyKey = propertyKey.replace('_', ' ').toUpperCase();
    const nestedValue = value[propertyKey];
    const nestedSchema = createNestedSchema(propertyKey, schemaProperties);

    return (
        <div className={classes.container}>
            <div className={classes.title}>{title || displayPropertyKey}</div>
            <PartnerFieldSchemaValue
                value={nestedValue}
                jsonSchema={nestedSchema}
                partnerConfigFields={partnerConfigFields}
            />
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
