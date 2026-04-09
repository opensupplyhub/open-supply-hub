import React from 'react';
import { string, object, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { getDescription, getAbsoluteUri, getDisplayLinkText } from './utils';
import { getLinkTextFromSchema } from '../../utils';
import { commonPropertyStyles } from '../../styles';
import { sendLocationPartnerExternalLinkClick } from '../../../../util/analytics/gaCustomEvents';

const UriReferenceProperty = ({
    propertyKey,
    value,
    schemaProperties: incomingSchemaProperties,
    partnerConfigFields: incomingPartnerConfigFields,
    classes,
    gaSpotlightAnalytics,
}) => {
    const propertyValue = value[propertyKey];

    if (!propertyValue) {
        return null;
    }

    const schemaProperties = incomingSchemaProperties || {};
    const partnerConfigFields = incomingPartnerConfigFields || {};
    const description = getDescription(propertyKey, schemaProperties);
    const linkText = getLinkTextFromSchema(
        propertyKey,
        value,
        schemaProperties,
        propertyValue,
    );

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

    const handleExternalClick = () => {
        if (!gaSpotlightAnalytics) {
            return;
        }
        sendLocationPartnerExternalLinkClick({
            contributorName: gaSpotlightAnalytics.contributor_name,
            partnerGroup: gaSpotlightAnalytics.partner_group,
            linkPlacement: gaSpotlightAnalytics.link_placement,
            destinationUrl: absoluteUri,
            osId: gaSpotlightAnalytics.os_id,
            partnerFieldName: gaSpotlightAnalytics.partner_field_name,
            userId: gaSpotlightAnalytics.user_id,
        });
    };

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
                className={classes.link}
                onClick={handleExternalClick}
            >
                <span>{displayLinkText}</span>
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
    gaSpotlightAnalytics: object,
};

UriReferenceProperty.defaultProps = {
    schemaProperties: {},
    partnerConfigFields: null,
    gaSpotlightAnalytics: null,
};

export default withStyles(commonPropertyStyles)(UriReferenceProperty);
