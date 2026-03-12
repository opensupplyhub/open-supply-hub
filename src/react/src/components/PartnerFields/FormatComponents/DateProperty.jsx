import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema, getFormattedDateValue } from '../utils';
import { commonPropertyStyles } from '../styles';
import PartnerFieldLabel from '../PartnerFieldLabel/PartnerFieldLabel';

const DateProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const formattedDate = getFormattedDateValue(propertyKey, value, 'LL');

    return (
        <div className={classes.container}>
            {title && <PartnerFieldLabel title={title} />}
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
