import React from 'react';
import PropTypes from 'prop-types';
import { Link as RouterLink } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

const ClaimSubtitleRow = ({
    classes,
    claimFacilityLink,
    isClaimed,
    isPending,
    contributorName,
    formattedDate,
}) => {
    const showClaimLink = !isClaimed && !isPending;
    const showClaimedByLine = isClaimed && (contributorName || formattedDate);

    if (!showClaimLink && !showClaimedByLine) return null;

    const subtitleContent = showClaimLink ? (
        <Typography component="p" variant="body1" className={classes.subtitle}>
            <RouterLink
                to={claimFacilityLink}
                href={claimFacilityLink}
                className={classes.link}
            >
                I want to claim this production location
            </RouterLink>
        </Typography>
    ) : (
        <Typography component="p" variant="body1" className={classes.subtitle}>
            {contributorName && formattedDate && (
                <>
                    <span className={classes.subtitleSameLine}>
                        Claimed by{' '}
                        <Typography
                            component="span"
                            className={classes.inlineHighlight}
                        >
                            {contributorName}
                        </Typography>
                    </span>{' '}
                    on{' '}
                    <Typography
                        component="span"
                        className={classes.inlineHighlight}
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
                        className={classes.inlineHighlight}
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
                        className={classes.inlineHighlight}
                    >
                        {formattedDate}
                    </Typography>
                </>
            )}
        </Typography>
    );

    return (
        <Grid item xs={12} className={classes.subtitleRow}>
            <Grid
                container
                spacing={0}
                wrap="nowrap"
                className={classes.row}
                alignItems="center"
            >
                <Grid item className={classes.iconColumn} />
                <Grid item className={classes.statusContent}>
                    {subtitleContent}
                </Grid>
            </Grid>
        </Grid>
    );
};

ClaimSubtitleRow.propTypes = {
    classes: PropTypes.object.isRequired,
    claimFacilityLink: PropTypes.string.isRequired,
    isClaimed: PropTypes.bool.isRequired,
    isPending: PropTypes.bool.isRequired,
    contributorName: PropTypes.string,
    formattedDate: PropTypes.string,
};

ClaimSubtitleRow.defaultProps = {
    contributorName: null,
    formattedDate: null,
};

export default ClaimSubtitleRow;
