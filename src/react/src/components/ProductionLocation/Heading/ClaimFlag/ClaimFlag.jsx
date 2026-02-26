import React from 'react';
import PropTypes from 'prop-types';
import { Link as RouterLink } from 'react-router-dom';
import { connect } from 'react-redux';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';
import InfoIcon from '@material-ui/icons/Info';
import Business from '@material-ui/icons/Business';

import BadgeClaimed from '../../../BadgeClaimed';
import DialogTooltip from '../../../Contribute/DialogTooltip';

import {
    makeClaimFacilityLinkWithFeatureFlag,
    convertFeatureFlagsObjectToListOfActiveFlags,
} from '../../../../util/util';
import { ENABLE_V1_CLAIMS_FLOW } from '../../../../util/constants';

import { getBackgroundColorClass, getMainText, formatClaimDate } from './utils';
import styles from './styles';

const FacilityDetailsClaimFlag = ({
    classes,
    osId,
    isClaimed,
    isPending,
    isEmbed,
    isV1ClaimsFlowEnabled,
    claimInfo,
}) => {
    if (isEmbed) return null;

    const variant = getBackgroundColorClass(isClaimed, isPending);
    const suffix = variant.replace('root', '');
    const rootClass = [classes.root, classes[variant]]
        .filter(Boolean)
        .join(' ');
    const iconClass = classes[`icon${suffix}`];
    const statusTextClass = [
        classes.statusText,
        classes[`statusText${suffix}`],
    ].join(' ');

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
    const showClaimedByLine = isClaimed && (contributorName || formattedDate);

    const claimedProfileTooltipText =
        "This profile has been claimed and verified by the production location's owner or manager. Claimed data is considered the most authoritative source.\n\nLearn more →";

    return (
        <Grid
            container
            direction="column"
            className={rootClass}
            data-testid="claim-banner"
        >
            <Grid item xs={12}>
                <Grid
                    container
                    alignItems="center"
                    wrap="nowrap"
                    className={classes.row}
                >
                    <Grid item className={iconClass}>
                        {isClaimed || isPending ? (
                            <BadgeClaimed fontSize="24px" />
                        ) : (
                            <Business
                                style={{
                                    fontSize: 24,
                                    display: 'block',
                                }}
                            />
                        )}
                    </Grid>
                    <Grid item className={classes.statusContent}>
                        <div className={classes.statusRow}>
                            <Typography className={statusTextClass}>
                                {getMainText(isClaimed, isPending)}
                            </Typography>
                            {(isClaimed || isPending) && (
                                <DialogTooltip
                                    text={claimedProfileTooltipText}
                                    childComponent={
                                        <IconButton
                                            className={classes.infoButton}
                                            size="small"
                                            aria-label="More information"
                                            disableRipple
                                        >
                                            <InfoIcon
                                                style={{
                                                    width: 16,
                                                    height: 16,
                                                }}
                                            />
                                        </IconButton>
                                    }
                                />
                            )}
                        </div>
                        {!isClaimed && !isPending && (
                            <Typography component="p" variant="body1">
                                <RouterLink
                                    to={claimFacilityLink}
                                    href={claimFacilityLink}
                                    className={classes.link}
                                >
                                    I want to claim this production location
                                </RouterLink>
                            </Typography>
                        )}
                        {showClaimedByLine && (
                            <Typography
                                className={classes.subtitle}
                                component="p"
                                variant="body1"
                            >
                                {contributorName && formattedDate && (
                                    <>
                                        <span
                                            className={classes.subtitleSameLine}
                                        >
                                            Claimed by{' '}
                                            <Typography
                                                component="span"
                                                className={
                                                    classes.subtitleHighlight
                                                }
                                            >
                                                {contributorName}
                                            </Typography>
                                        </span>{' '}
                                        on{' '}
                                        <Typography
                                            component="span"
                                            className={
                                                classes.subtitleHighlight
                                            }
                                        >
                                            {formattedDate}
                                        </Typography>
                                    </>
                                )}
                                {contributorName && !formattedDate && (
                                    <span className={classes.subtitleSameLine}>
                                        Claimed by{' '}
                                        <Typography
                                            component="span"
                                            className={
                                                classes.subtitleHighlight
                                            }
                                        >
                                            {contributorName}
                                        </Typography>
                                    </span>
                                )}
                                {!contributorName && formattedDate && (
                                    <>
                                        Claimed on{' '}
                                        <Typography
                                            component="span"
                                            className={
                                                classes.subtitleHighlight
                                            }
                                        >
                                            {formattedDate}
                                        </Typography>
                                    </>
                                )}
                            </Typography>
                        )}
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    );
};

FacilityDetailsClaimFlag.propTypes = {
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
    }),
};

FacilityDetailsClaimFlag.defaultProps = {
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
    withStyles(styles)(FacilityDetailsClaimFlag),
);
