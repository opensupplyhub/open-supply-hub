import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';

import ShowOnly from './ShowOnly';
import BadgeVerified from './BadgeVerified';
import FeatureFlag from './FeatureFlag';

import { CLAIM_A_FACILITY } from '../util/constants';

const detailsStyles = theme =>
    Object.freeze({
        root: {
            display: 'flex',
            alignItems: 'center',
        },
        badgeWrapper: {
            paddingRight: theme.spacing.unit,
            paddingTop: theme.spacing.unit,
        },
        primaryText: {
            wordWrap: 'break-word',
            fontWeight: 500,
            fontSize: '18px',
            lineHeight: '21px',
            paddingTop: theme.spacing.unit,
        },
        secondaryText: {
            wordWrap: 'break-word',
            fontWeight: 500,
            fontSize: '14px',
            lineHeight: '17px',
            paddingTop: theme.spacing.unit,
        },
    });

const CLAIM_EXPLANATORY_TEXT =
    'Please note: The OS Hub team has only verified that the person claiming a ' +
    'facility profile is connected to that facility. The OS Hub team has not ' +
    'verified any additional details added to a facility profile, e.g. ' +
    'certifications, production capabilities etc. Users interested in those ' +
    'details will need to carry out their own due diligence checks.';

const FacilityDetailsDetail = ({
    primary,
    locationLabeled,
    secondary,
    isVerified,
    isFromClaim,
    classes,
}) => (
    <div className={classes.root} data-testid="facility-details-detail">
        <ShowOnly when={isVerified || isFromClaim}>
            <div className={classes.badgeWrapper}>
                <ShowOnly when={isVerified && !isFromClaim}>
                    <BadgeVerified />
                </ShowOnly>
                <FeatureFlag flag={CLAIM_A_FACILITY}>
                    <ShowOnly when={isFromClaim}>
                        <Tooltip title={CLAIM_EXPLANATORY_TEXT}>
                            <BadgeVerified />
                        </Tooltip>
                    </ShowOnly>
                </FeatureFlag>
            </div>
        </ShowOnly>
        <div>
            <Typography className={classes.primaryText}>
                {primary || locationLabeled}
            </Typography>
            {secondary ? (
                <Typography className={classes.secondaryText}>
                    {secondary}
                </Typography>
            ) : null}
        </div>
    </div>
);

export default withStyles(detailsStyles)(FacilityDetailsDetail);
