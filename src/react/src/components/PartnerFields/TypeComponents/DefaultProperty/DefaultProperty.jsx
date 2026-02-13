import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema } from '../../utils';
import getPropertyValueAsString from './utils';
import { commonPropertyStyles } from '../../styles';

const DefaultProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const stringValue = getPropertyValueAsString(propertyKey, value);

    return (
        <div className={classes.container}>
            {title && `${title}: `}
            {stringValue}
        </div>
    );
};

DefaultProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(commonPropertyStyles)(DefaultProperty);
