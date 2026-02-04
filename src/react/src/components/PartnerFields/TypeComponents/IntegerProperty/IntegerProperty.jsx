import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getPropertyValue, getTitleFromSchema } from './utils';
import integerPropertyStyles from './styles';

/**
 * Component for rendering integer type properties.
 */
const IntegerProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const propertyValue = getPropertyValue(propertyKey, value);

    if (!title) {
        return <div className={classes.container}>{propertyValue}</div>;
    }

    return (
        <div className={classes.container}>
            <strong>{title}:</strong> {propertyValue}
        </div>
    );
};

IntegerProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(integerPropertyStyles)(IntegerProperty);
