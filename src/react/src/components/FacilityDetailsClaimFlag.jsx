import React from 'react';
import { Link } from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import Icon from '@material-ui/core/Icon';
import { withStyles } from '@material-ui/core/styles';

import BadgeClaimed from './BadgeClaimed';
import COLOURS from '../util/COLOURS';

import { makeClaimFacilityLink } from '../util/util';

const claimFlagBaseStyles = theme =>
    Object.freeze({
        root: {
            backgroundColor: COLOURS.LIGHT_RED,
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            paddingRight: theme.spacing.unit,
            paddingBottom: theme.spacing.unit,
        },
        link: {
            color: theme.palette.primary.main,
        },
        itemPadding: {
            paddingLeft: theme.spacing.unit * 3,
            paddingTop: theme.spacing.unit,
            paddingBottom: theme.spacing.unit / 4,
        },
    });

const getBackgroundColor = (isClaimed, isPending) => {
    if (isClaimed) {
        return COLOURS.GREEN;
    }
    if (isPending) {
        return COLOURS.NAVIGATION;
    }
    return COLOURS.LIGHT_RED;
};

const getMainText = (isClaimed, isPending) => {
    if (isClaimed) {
        return 'This production location has been claimed by an owner or manager';
    }
    if (isPending) {
        return 'There is a pending claim for this production location';
    }
    return 'This production location has not been claimed';
};

const FacilityDetailsClaimFlag = ({
    classes,
    osId,
    isClaimed,
    isPending,
    isEmbed,
}) => {
    if (isEmbed) return null;
    const backgroundColor = getBackgroundColor(isClaimed, isPending);
    const claimFacilityLink = makeClaimFacilityLink(osId);
    return (
        <div
            className={classes.root}
            style={{ backgroundColor }}
            data-testid="claim-banner"
        >
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

export default withStyles(claimFlagBaseStyles)(FacilityDetailsClaimFlag);
