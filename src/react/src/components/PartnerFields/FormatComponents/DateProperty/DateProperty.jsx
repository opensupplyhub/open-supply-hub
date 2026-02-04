import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema } from '../../utils';
import getFormattedDateValue from './utils';
import { commonPropertyStyles } from '../../styles';

const DateProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const formattedDate = getFormattedDateValue(propertyKey, value);

    return (
        <div className={classes.container}>
            {title && `${title}: `}
            {formattedDate}
        </div>
    );
};

DateProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(commonPropertyStyles)(DateProperty);
