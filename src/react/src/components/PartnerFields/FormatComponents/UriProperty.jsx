import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema, getLinkTextFromSchema } from '../utils';
import { commonPropertyStyles } from '../styles';

const UriProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const propertyValue = value[propertyKey];

    if (!propertyValue) {
        return null;
    }

    const linkText = getLinkTextFromSchema(
        propertyKey,
        value,
        schemaProperties,
    );

    return (
        <div className={classes.container}>
            {title && `${title}: `}
            <a
                key={`${propertyKey}-uri-${propertyValue}`}
                href={propertyValue}
                target="_blank"
                rel="noopener noreferrer"
            >
                {linkText}
            </a>
        </div>
    );
};

UriProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(commonPropertyStyles)(UriProperty);
