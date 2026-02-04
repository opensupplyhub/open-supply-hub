import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema } from '../../utils';
import getPropertyValue from './utils';
import { commonPropertyStyles } from '../../styles';

const IntegerProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const propertyValue = getPropertyValue(propertyKey, value);

    return (
        <div className={classes.container}>
            {title && `${title}: `}
            {propertyValue}
        </div>
    );
};

IntegerProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(commonPropertyStyles)(IntegerProperty);
