import React from 'react';
import { object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import { claimCampaignBannerStyles } from './styles';

// ClaimIntro only passes a code the backend has just confirmed belongs to
// an active campaign (with the claim_campaigns flag on), so an empty code
// is the single gate here: an invalid, closed or unchecked code is never
// shown as an invitation.
const ClaimCampaignBanner = ({ classes, campaignCode }) => {
    if (!campaignCode) {
        return null;
    }

    return (
        <div className={classes.banner}>
            <Typography>
                This claim is part of a claims campaign (code{' '}
                <span className={classes.code}>{campaignCode}</span>
                ). Your progress will be visible to the campaign organizer.
            </Typography>
        </div>
    );
};

ClaimCampaignBanner.defaultProps = {
    campaignCode: '',
};

ClaimCampaignBanner.propTypes = {
    campaignCode: string,
    classes: object.isRequired,
};

export default withStyles(claimCampaignBannerStyles)(ClaimCampaignBanner);
