import React from 'react';
import moment from 'moment';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import {
    GA_LINK_PLACEMENT,
    sendLocationPartnerProfileLinkClick,
} from '../../../../util/analytics/gaCustomEvents';
import styles from './styles';

const ContributorLink = ({ classes, gaSpotlightContext, ...props }) => {
    const profilePath = `/profile/${props.contributor_id}`;

    const handleProfileClick = () => {
        if (!gaSpotlightContext) {
            return;
        }
        const destinationUrl =
            typeof window !== 'undefined'
                ? `${window.location.origin}${profilePath}`
                : profilePath;
        sendLocationPartnerProfileLinkClick({
            contributorName: props.contributor_name,
            partnerGroup: gaSpotlightContext.partner_group,
            linkPlacement: GA_LINK_PLACEMENT.CONTRIBUTION_LINE,
            destinationUrl,
            osId: gaSpotlightContext.os_id,
            partnerFieldName: gaSpotlightContext.partner_field_name,
            userId:
                props.contributor_id != null
                    ? String(props.contributor_id)
                    : '',
        });
    };

    return (
        <>
            {moment(props.created_at).format('LL')} by{' '}
            <a
                href={profilePath}
                target="_blank"
                rel="noopener noreferrer"
                className={classes.contributorLink}
                onClick={handleProfileClick}
            >
                {props.contributor_name}
            </a>
        </>
    );
};

ContributorLink.propTypes = {
    classes: PropTypes.object.isRequired,
    created_at: PropTypes.string,
    contributor_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    contributor_name: PropTypes.string,
    gaSpotlightContext: PropTypes.object,
};

ContributorLink.defaultProps = {
    gaSpotlightContext: null,
    created_at: undefined,
    contributor_id: undefined,
    contributor_name: undefined,
};

export default withStyles(styles)(ContributorLink);
