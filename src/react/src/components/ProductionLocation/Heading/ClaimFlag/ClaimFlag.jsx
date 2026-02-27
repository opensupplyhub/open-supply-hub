import React from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import Icon from '@material-ui/core/Icon';
import { withStyles } from '@material-ui/core/styles';

import BadgeClaimed from '../../../BadgeClaimed';

import {
    makeClaimFacilityLinkWithFeatureFlag,
    convertFeatureFlagsObjectToListOfActiveFlags,
} from '../../../../util/util';
import { ENABLE_V1_CLAIMS_FLOW } from '../../../../util/constants';

import { getBackgroundColorClass, getMainText } from './utils';
import facilityDetailsClaimFlagStyles from './styles';

const FacilityDetailsClaimFlag = ({
    classes,
    osId,
    isClaimed,
    isPending,
    isEmbed,
    isV1ClaimsFlowEnabled,
}) => {
    if (isEmbed) return null;
    const rootVariantClass =
        classes[getBackgroundColorClass(isClaimed, isPending)];
    const claimFacilityLink = makeClaimFacilityLinkWithFeatureFlag(
        osId,
        isV1ClaimsFlowEnabled,
    );
    return (
        <div className={rootVariantClass} data-testid="claim-banner">
            <div className={classes.contentContainer}>
                <Icon className={classes.itemPadding}>
                    <BadgeClaimed />
                </Icon>
                <Typography className={classes.itemPadding}>
                    {getMainText(isClaimed, isPending)}
                </Typography>
                {!isClaimed && !isPending ? (
                    <Typography className={classes.itemPadding}>
                        <Link
                            to={claimFacilityLink}
                            href={claimFacilityLink}
                            className={classes.link}
                        >
                            I want to claim this production location
                        </Link>
                    </Typography>
                ) : null}
            </div>
        </div>
    );
};

const mapStateToProps = ({ featureFlags: { flags } }) => {
    const activeFeatureFlags = convertFeatureFlagsObjectToListOfActiveFlags(
        flags,
    );
    return {
        isV1ClaimsFlowEnabled: activeFeatureFlags.includes(
            ENABLE_V1_CLAIMS_FLOW,
        ),
    };
};

export default connect(mapStateToProps)(
    withStyles(facilityDetailsClaimFlagStyles)(FacilityDetailsClaimFlag),
);
