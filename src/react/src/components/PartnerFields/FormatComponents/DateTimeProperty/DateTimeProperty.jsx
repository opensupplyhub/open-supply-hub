import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema } from '../../utils';
import getFormattedDateTimeValue from './utils';
import { commonPropertyStyles } from '../../styles';

const DateTimeProperty = ({
    propertyKey,
    value,
    schemaProperties,
    classes,
}) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const formattedDateTime = getFormattedDateTimeValue(propertyKey, value);

    return (
        <div className={classes.container}>
            {title && `${title}: `}
            {formattedDateTime}
        </div>
    );
};

DateTimeProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(commonPropertyStyles)(DateTimeProperty);
