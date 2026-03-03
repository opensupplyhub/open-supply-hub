import React from 'react';
import PropTypes from 'prop-types';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import InfoIcon from '@material-ui/icons/Info';

import BadgeClaimed from '../../../BadgeClaimed';
import DialogTooltip from '../../../Contribute/DialogTooltip';

import { getMainText, getClaimFlagStateClassName } from './utils';
import {
    CLAIMED_PROFILE_TOOLTIP_TEXT,
    CLAIM_LEARN_MORE_URL,
} from './constants';

const ClaimStatusRow = ({ classes, isClaimed, isPending }) => {
    const iconColumnClassName = getClaimFlagStateClassName(
        classes,
        isClaimed,
        isPending,
        {
            base: 'iconColumn',
            claimed: 'iconClaimed',
            pending: 'iconPending',
            unclaimed: 'iconUnclaimed',
        },
    );
    const statusTextClassName = getClaimFlagStateClassName(
        classes,
        isClaimed,
        isPending,
        {
            base: 'statusText',
            claimed: 'statusTextClaimed',
            pending: 'statusTextPending',
            unclaimed: 'statusTextUnclaimed',
        },
    );
    return (
        <Grid item xs={12}>
            <Grid
                container
                spacing={0}
                alignItems="center"
                wrap="nowrap"
                className={classes.row}
            >
                <Grid item className={iconColumnClassName}>
                    <BadgeClaimed fontSize="24px" />
                </Grid>
                <Grid item className={classes.statusContent}>
                    <div className={classes.statusRow}>
                        <Typography
                            component="h4"
                            className={statusTextClassName}
                        >
                            {getMainText(isClaimed, isPending)}
                        </Typography>
                        {isClaimed && (
                            <DialogTooltip
                                text={CLAIMED_PROFILE_TOOLTIP_TEXT}
                                textHref={
                                    <p
                                        style={{
                                            marginTop: 8,
                                            marginBottom: 0,
                                        }}
                                    >
                                        <a
                                            href={CLAIM_LEARN_MORE_URL}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{ color: 'white' }}
                                        >
                                            Learn more →
                                        </a>
                                    </p>
                                }
                                interactive
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
                </Grid>
            </Grid>
        </Grid>
    );
};

ClaimStatusRow.propTypes = {
    classes: PropTypes.object.isRequired,
    isClaimed: PropTypes.bool.isRequired,
    isPending: PropTypes.bool.isRequired,
};

export default ClaimStatusRow;
