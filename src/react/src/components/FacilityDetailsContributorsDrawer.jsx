import React from 'react';
import { Link } from 'react-router-dom';
import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import { withStyles } from '@material-ui/core/styles';

import ShowOnly from './ShowOnly';
import BadgeVerified from './BadgeVerified';
import GroupIcon from './GroupIcon';

import { makeProfileRouteLink } from '../util/util';

const contributorsDrawerStyles = theme =>
    Object.freeze({
        drawerHeader: {
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
        },
        currentContributorsWrapper: {
            marginBottom: '2rem',
        },
        drawerTitle: {
            marginBottom: '2rem',
            fontWeight: 900,
            fontSize: '2rem',
        },
        drawerTitleText: {
            paddingLeft: theme.spacing.unit,
        },
        drawerContent: {
            padding: '1rem 4.5rem',
            maxWidth: '560px',
            minWidth: '33%',
        },
        contributor: {
            boxShadow: '0px 1px 0px 0px rgb(240, 240, 240)',
            paddingTop: theme.spacing.unit,
            paddingBottom: theme.spacing.unit,
        },
        primaryText: {
            overflowWrap: 'break-word',
        },
        link: {
            color: theme.palette.primary.main,
            textDecoration: 'none',
        },
    });

const FacilityDetailsContributorsDrawer = ({
    classes,
    open,
    onClose,
    splittedContributors,
}) => (
    <Drawer anchor="right" open={open} onClose={onClose}>
        <div className={classes.drawerContent}>
            <div className={classes.drawerHeader}>
                <IconButton aria-label="Close" onClick={onClose}>
                    <CloseIcon />
                </IconButton>
            </div>
            {!!splittedContributors.publicContributors.length && (
                <div className={classes.currentContributorsWrapper}>
                    <Typography className={classes.drawerTitle}>
                        <GroupIcon />{' '}
                        <span className={classes.drawerTitleText}>
                            Current Contributors (
                            {splittedContributors.publicContributors.length})
                        </span>
                    </Typography>
                    {splittedContributors.publicContributors.map(
                        contributor => (
                            <div
                                key={`${contributor.id} ${contributor.contributor_name}`}
                                className={classes.contributor}
                            >
                                <ShowOnly when={contributor.is_verified}>
                                    <BadgeVerified />
                                </ShowOnly>
                                <Link
                                    to={makeProfileRouteLink(contributor.id)}
                                    className={`${classes.primaryText} ${classes.link}`}
                                >
                                    {contributor.contributor_name}
                                </Link>
                                {contributor.list_names.map((listName, i) => (
                                    <Typography
                                        key={`${
                                            contributor.id + i
                                        } ${listName}`}
                                    >
                                        {listName}
                                    </Typography>
                                ))}
                            </div>
                        ),
                    )}
                </div>
            )}
            {!!splittedContributors.nonPublicContributors.length && (
                <div>
                    <Typography className={classes.drawerTitle}>
                        <GroupIcon />{' '}
                        <span className={classes.drawerTitleText}>
                            Other Contributors
                        </span>
                    </Typography>
                    {splittedContributors.nonPublicContributors.map(
                        contributor => (
                            <div
                                key={contributor.name}
                                className={classes.contributor}
                            >
                                <Typography className={classes.primaryText}>
                                    {contributor.name}
                                </Typography>
                            </div>
                        ),
                    )}
                </div>
            )}
        </div>
    </Drawer>
);

export default withStyles(contributorsDrawerStyles)(
    FacilityDetailsContributorsDrawer,
);
