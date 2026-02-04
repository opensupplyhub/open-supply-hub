import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getPropertyValueAsString, getTitleFromSchema } from './utils';
import defaultPropertyStyles from './styles';

/**
 * Component for rendering default format properties (no format or unsupported format).
 */
const DefaultProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const stringValue = getPropertyValueAsString(propertyKey, value);

    if (!title) {
        return <div className={classes.container}>{stringValue}</div>;
    }

    return (
        <div className={classes.container}>
            <strong>{title}:</strong> {stringValue}
        </div>
    );
};

DefaultProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(defaultPropertyStyles)(DefaultProperty);
