import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import {
    constructUrlFromPartnerField,
    showFieldDefaultDisplayText,
} from './utils';

/**
 * Component for rendering URI-reference format properties.
 */
const UriReferenceProperty = ({
    propertyKey,
    value,
    schemaProperties,
    partnerConfigFields,
    classes,
}) => {
    const propertyValue = value[propertyKey];
    if (!propertyValue) {
        return null;
    }

    const textKey = `${propertyKey}_text`;
    const textPropertyDefined = schemaProperties && schemaProperties[textKey];

    const {
        value: { description },
    } = schemaProperties;

    const linkText =
        textPropertyDefined && textKey in value
            ? value[textKey]
            : propertyValue;

    const { baseUrl, displayText } = partnerConfigFields;

    let absoluteURI;
    if (baseUrl) {
        absoluteURI = constructUrlFromPartnerField(baseUrl, linkText);
    }

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
                    ? displayText || absoluteURI
                    : showFieldDefaultDisplayText(
                          schemaProperties,
                          propertyValue,
                          propertyKey,
                      )}
            </a>
        </>
    );
};

export default withStyles()(UriReferenceProperty);
