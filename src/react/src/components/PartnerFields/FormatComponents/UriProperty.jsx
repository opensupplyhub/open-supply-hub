import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { getTitleFromSchema, getLinkTextFromSchema } from '../utils';
import { commonPropertyStyles } from '../styles';
import PartnerFieldLabel from '../PartnerFieldLabel/PartnerFieldLabel';
import { sendLocationPartnerExternalLinkClick } from '../../../util/analytics/gaCustomEvents';
import useViewerUserIdForAnalytics from '../../../util/analytics/hooks';

const UriProperty = ({
    propertyKey,
    value,
    schemaProperties,
    classes,
    gaSpotlightAnalytics,
}) => {
    const viewerUserId = useViewerUserIdForAnalytics();
    const title = getTitleFromSchema(propertyKey, schemaProperties);
    const schemaProperty = schemaProperties[propertyKey] || {};
    const propertyValue = value[propertyKey] || schemaProperty.default;

    if (!propertyValue) {
        return null;
    }

    const linkText = getLinkTextFromSchema(
        propertyKey,
        value,
        schemaProperties,
        propertyValue,
    );

    const handleExternalClick = () => {
        if (!gaSpotlightAnalytics) {
            return;
        }
        sendLocationPartnerExternalLinkClick({
            contributorName: gaSpotlightAnalytics.contributor_name,
            partnerGroup: gaSpotlightAnalytics.partner_group,
            linkPlacement: gaSpotlightAnalytics.link_placement,
            destinationUrl: propertyValue,
            osId: gaSpotlightAnalytics.os_id,
            partnerFieldName: gaSpotlightAnalytics.partner_field_name,
            userId: gaSpotlightAnalytics.user_id,
            viewerUserId,
        });
    };

    return (
        <div className={classes.container}>
            {title && <PartnerFieldLabel title={title} />}
            <a
                key={`${propertyKey}-uri-${propertyValue}`}
                href={propertyValue}
                target="_blank"
                rel="noopener noreferrer"
                className={classes.link}
                onClick={handleExternalClick}
            >
                <span>{linkText}</span>
            </a>
        </div>
    );
};

UriProperty.propTypes = {
    propertyKey: string.isRequired,
    value: object.isRequired,
    schemaProperties: object.isRequired,
    classes: object.isRequired,
    gaSpotlightAnalytics: object,
};

UriProperty.defaultProps = {
    gaSpotlightAnalytics: null,
};

export default withStyles(commonPropertyStyles)(UriProperty);
