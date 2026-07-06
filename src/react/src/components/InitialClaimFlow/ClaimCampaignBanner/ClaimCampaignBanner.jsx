import React from 'react';
import { object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import { claimCampaignBannerStyles } from './styles';

// The campaign code only enters the claim form state when the
// claim_campaigns feature flag is active (see ClaimIntro), so an empty
// code is the single gate here.
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
