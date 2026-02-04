import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getLinkText, getTitleFromSchema, getPropertyValue } from './utils';
import uriPropertyStyles from './styles';

/**
 * Component for rendering URI format properties.
 */
const UriProperty = ({ propertyKey, value, schemaProperties, classes }) => {
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const propertyValue = getPropertyValue(propertyKey, value);

    if (!propertyValue) {
        return null;
    }

    const linkText = getLinkText(propertyKey, value, schemaProperties);

    if (!title) {
        return (
            <div className={classes.container}>
                <a
                    key={`${propertyKey}-uri-${propertyValue}`}
                    href={propertyValue}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={classes.link}
                >
                    {linkText}
                </a>
            </div>
        );
    }

    return (
        <div className={classes.container}>
            <div>
                <strong>{title}:</strong>
            </div>
            <div>
                <a
                    key={`${propertyKey}-uri-${propertyValue}`}
                    href={propertyValue}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={classes.link}
                >
                    {linkText}
                </a>
            </div>
        </div>
    );
};

UriProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(uriPropertyStyles)(UriProperty);
