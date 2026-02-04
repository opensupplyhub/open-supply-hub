import React from 'react';
import { string, object, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import {
    getPropertyValue,
    getDescription,
    getLinkText,
    getAbsoluteUri,
    getDisplayLinkText,
} from './utils';
import { commonPropertyStyles } from '../../styles';

const UriReferenceProperty = ({
    propertyKey,
    value,
    schemaProperties: incomingSchemaProperties,
    partnerConfigFields: incomingPartnerConfigFields,
    classes,
}) => {
    const propertyValue = getPropertyValue(propertyKey, value);
    if (!propertyValue) {
        return null;
    }

    const schemaProperties = incomingSchemaProperties || {};
    const partnerConfigFields = incomingPartnerConfigFields || {};
    const description = getDescription(propertyKey, schemaProperties);
    const linkText = getLinkText(propertyKey, value, schemaProperties);

    const { baseUrl, displayText } = partnerConfigFields;
    const absoluteUri = getAbsoluteUri(baseUrl, propertyValue);
    const displayLinkText = getDisplayLinkText(
        baseUrl,
        displayText,
        linkText,
        absoluteUri,
        schemaProperties,
        propertyValue,
        propertyKey,
    );

    return (
        <div className={classes.container}>
            {description ? (
                <Typography variant="body2" component="div">
                    {description}
                </Typography>
            ) : null}
            <a
                key={`${propertyKey}-uri-${propertyValue}`}
                href={absoluteUri}
                target="_blank"
                rel="noopener noreferrer"
            >
                {displayLinkText}
            </a>
        </div>
    );
};

UriReferenceProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object,
    partnerConfigFields: shape({
        baseUrl: string,
        displayText: string,
    }),
    classes: object.isRequired,
};

UriReferenceProperty.defaultProps = {
    schemaProperties: {},
    partnerConfigFields: null,
};

export default withStyles(commonPropertyStyles)(UriReferenceProperty);
