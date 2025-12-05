import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import {
    constructUrlFromPartnerField,
    showFieldDefaultDisplayText,
} from './utils';

const styles = () => ({});

/**
 * Component for rendering URI-reference format properties.
 */
const UriReferenceProperty = ({
    propertyKey,
    value,
    schemaProperties: incomingSchemaProperties,
    partnerConfigFields: incomingPartnerConfigFields,
    classes,
}) => {
    const propertyValue = value[propertyKey];
    if (!propertyValue) {
        return null;
    }

    const schemaProperties = incomingSchemaProperties || {};
    const partnerConfigFields = incomingPartnerConfigFields || {};
    const textKey = `${propertyKey}_text`;
    const textPropertyDefined = !!schemaProperties[textKey];
    const { description } = schemaProperties[propertyKey] || {};

    const linkText =
        textPropertyDefined && textKey in value
            ? value[textKey]
            : propertyValue;

    const { baseUrl, displayText } = partnerConfigFields;

    const absoluteURI = baseUrl
        ? constructUrlFromPartnerField(baseUrl, propertyValue)
        : undefined;

    return (
        <>
            {description ? (
                <Typography className={classes.primaryText} variant="div">
                    {description}
                </Typography>
            ) : null}
            <a
                key={`${propertyKey}-uri-${propertyValue}`}
                href={absoluteURI}
                target="_blank"
                rel="noopener noreferrer"
            >
                {baseUrl
                    ? displayText || linkText || absoluteURI
                    : showFieldDefaultDisplayText(
                          schemaProperties,
                          propertyValue,
                          propertyKey,
                      )}
            </a>
        </>
    );
};

export default withStyles(styles)(UriReferenceProperty);
