import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import {
    makeClaimFacilityLinkWithFeatureFlag,
    convertFeatureFlagsObjectToListOfActiveFlags,
} from '../../../../util/util';
import { ENABLE_V1_CLAIMS_FLOW } from '../../../../util/constants';

import { formatClaimDate } from './utils';
import ClaimStatusRow from './ClaimStatusRow';
import ClaimSubtitleRow from './ClaimSubtitleRow';
import productionLocationDetailsClaimFlagStyles from './styles';

const ClaimFlag = ({
    classes,
    osId,
    isClaimed,
    isPending,
    isEmbed,
    isV1ClaimsFlowEnabled,
    claimInfo,
}) => {
    if (isEmbed) return null;

    const claimFacilityLink = makeClaimFacilityLinkWithFeatureFlag(
        osId,
        isV1ClaimsFlowEnabled,
    );
    const contributorName =
        typeof claimInfo?.contributor === 'string'
            ? claimInfo.contributor
            : claimInfo?.contributor?.name ?? null;
    const claimedAt = claimInfo?.approved_at ?? claimInfo?.created_at;
    const formattedDate = formatClaimDate(claimedAt);
    const showSubtitleRow =
        (!isClaimed && !isPending) ||
        (isClaimed && (contributorName || formattedDate));

    return (
        <Grid
            container
            direction="column"
            className={classes.root}
            data-testid="claim-banner"
        >
            <ClaimStatusRow
                classes={classes}
                isClaimed={isClaimed}
                isPending={isPending}
            />
            {showSubtitleRow && (
                <ClaimSubtitleRow
                    classes={classes}
                    claimFacilityLink={claimFacilityLink}
                    isClaimed={isClaimed}
                    isPending={isPending}
                    contributorName={contributorName}
                    formattedDate={formattedDate}
                />
            )}
        </Grid>
    );
};

ClaimFlag.propTypes = {
    classes: PropTypes.object.isRequired,
    osId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    isClaimed: PropTypes.bool.isRequired,
    isPending: PropTypes.bool.isRequired,
    isEmbed: PropTypes.bool,
    isV1ClaimsFlowEnabled: PropTypes.bool.isRequired,
    claimInfo: PropTypes.shape({
        contributor: PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.shape({ name: PropTypes.string }),
        ]),
        created_at: PropTypes.string,
        approved_at: PropTypes.string,
    }),
};

ClaimFlag.defaultProps = {
    isEmbed: false,
    claimInfo: null,
    osId: null,
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
    withStyles(productionLocationDetailsClaimFlagStyles)(ClaimFlag),
);
