import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getFormattedDateValue, getTitleFromSchema } from './utils';
import datePropertyStyles from './styles';

/**
 * Component for rendering date format properties.
 */
const DateProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const formattedDate = getFormattedDateValue(propertyKey, value);

    if (!title) {
        return <div className={classes.container}>{formattedDate}</div>;
    }

    return (
        <div className={classes.container}>
            <strong>{title}:</strong> {formattedDate}
        </div>
    );
};

DateProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(datePropertyStyles)(DateProperty);
