import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema, getFormattedDateValue } from '../utils';
import { commonPropertyStyles } from '../styles';
import PartnerFieldLabel from '../PartnerFieldLabel/PartnerFieldLabel';

const DateTimeProperty = ({
    propertyKey,
    value,
    schemaProperties,
    classes,
}) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const schemaProperty = schemaProperties[propertyKey] || {};
    const formattedDateTime =
        getFormattedDateValue(propertyKey, value, 'LLL') ||
        getFormattedDateValue(
            propertyKey,
            { [propertyKey]: schemaProperty.default },
            'LLL',
        );

    return (
        <div className={classes.container}>
            {title && <PartnerFieldLabel title={title} />}
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
