import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema, getLinkTextFromSchema } from '../utils';
import { commonPropertyStyles } from '../styles';

const UrlProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const propertyValue = value[propertyKey];

    if (!propertyValue) {
        return null;
    }

    const linkText = getLinkTextFromSchema(
        propertyKey,
        value,
        schemaProperties,
        propertyValue,
    );

    return (
        <div className={classes.container}>
            {title && `${title}: `}
            <a
                key={`${propertyKey}-url-${propertyValue}`}
                href={propertyValue}
                target="_blank"
                rel="noopener noreferrer"
            >
                {linkText}
            </a>
        </div>
    );
};

UrlProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(commonPropertyStyles)(UrlProperty);
