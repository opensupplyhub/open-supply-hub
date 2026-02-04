import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getFormattedDateTimeValue, getTitleFromSchema } from './utils';
import dateTimePropertyStyles from './styles';

/**
 * Component for rendering date-time format properties.
 */
const DateTimeProperty = ({
    propertyKey,
    value,
    schemaProperties,
    classes,
}) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const formattedDateTime = getFormattedDateTimeValue(propertyKey, value);

    if (!title) {
        return <div className={classes.container}>{formattedDateTime}</div>;
    }

    return (
        <div className={classes.container}>
            <strong>{title}:</strong> {formattedDateTime}
        </div>
    );
};

DateTimeProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(dateTimePropertyStyles)(DateTimeProperty);
