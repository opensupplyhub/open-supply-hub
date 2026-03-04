import React from 'react';
import { object, bool, func, arrayOf, shape, string, number } from 'prop-types';
import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Divider from '@material-ui/core/Divider';
import { withStyles } from '@material-ui/core/styles';
import CloseIcon from '@material-ui/icons/Close';
import PeopleOutlineIcon from '@material-ui/icons/PeopleOutline';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import ListIcon from '@material-ui/icons/List';
import { Link } from 'react-router-dom';

import { makeProfileRouteLink } from '../../../../util/util';
import {
    DRAWER_TITLE,
    ANONYMIZED_SECTION_TITLE,
    INFO_TEXT,
    LEARN_MORE_LABEL,
    LEARN_MORE_URL,
} from './constants';
import supplyChainNetworkDrawerStyles from './styles';

const SupplyChainNetworkDrawer = ({
    classes,
    open,
    onClose,
    totalCount,
    typeCounts,
    publicContributors,
    nonPublicContributors,
}) => (
    <Drawer
        anchor="right"
        open={open}
        onClose={onClose}
        classes={{ paper: classes.drawerPaper }}
    >
        <div className={classes.drawerContent}>
            <div className={classes.header}>
                <div className={classes.headerLeft}>
                    <PeopleOutlineIcon className={classes.titleIcon} />
                    <Typography className={classes.title} component="h2">
                        {DRAWER_TITLE}
                    </Typography>
                </div>
                <IconButton
                    className={classes.closeButton}
                    aria-label="Close"
                    onClick={onClose}
                >
                    <CloseIcon />
                </IconButton>
            </div>
            <Typography className={classes.subtitle} component="p">
                {totalCount} organizations have shared data about this
                production location
            </Typography>

            <div className={classes.infoBox}>
                <InfoOutlinedIcon className={classes.infoIcon} />
                <div>
                    <Typography className={classes.infoText} component="p">
                        {INFO_TEXT}
                    </Typography>
                    <a
                        href={LEARN_MORE_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={classes.learnMoreLink}
                    >
                        {LEARN_MORE_LABEL}
                    </a>
                </div>
            </div>

            {typeCounts.length > 0 && (
                <div className={classes.typeSummary}>
                    {typeCounts.map(({ type, count }) => (
                        <Typography
                            key={type}
                            className={classes.typeChip}
                            component="p"
                        >
                            {count} {type}
                        </Typography>
                    ))}
                </div>
            )}

            <Divider className={classes.divider} />

            {publicContributors.map(contributor => (
                <div key={contributor.id} className={classes.contributorEntry}>
                    <div className={classes.contributorNameRow}>
                        <Link
                            to={makeProfileRouteLink(contributor.id)}
                            className={classes.contributorName}
                        >
                            {contributor.contributor_name}
                        </Link>
                    </div>
                    {contributor.contributor_type && (
                        <Typography
                            className={classes.contributorType}
                            component="p"
                        >
                            {contributor.contributor_type}
                        </Typography>
                    )}
                    {/* list_names is built by splitContributorsIntoPublicAndNonPublic */}
                    {contributor.list_names &&
                        contributor.list_names.map(
                            listName =>
                                listName && (
                                    <div
                                        key={`${contributor.id}-${listName}`}
                                        className={classes.listEntry}
                                    >
                                        <ListIcon
                                            className={classes.listIcon}
                                        />
                                        <Typography
                                            className={classes.listName}
                                            component="span"
                                        >
                                            {listName}
                                        </Typography>
                                    </div>
                                ),
                        )}
                </div>
            ))}

            {nonPublicContributors.length > 0 && (
                <>
                    <div className={classes.sectionHeader}>
                        <PeopleOutlineIcon
                            className={classes.sectionHeaderIcon}
                        />
                        <Typography
                            className={classes.sectionTitle}
                            component="h3"
                        >
                            {ANONYMIZED_SECTION_TITLE}
                        </Typography>
                    </div>
                    {nonPublicContributors.map(contributor => (
                        <Typography
                            key={contributor.contributor_type}
                            className={classes.anonymizedType}
                            component="p"
                        >
                            {contributor.count} {contributor.contributor_type}
                        </Typography>
                    ))}
                </>
            )}
        </div>
    </Drawer>
);

SupplyChainNetworkDrawer.propTypes = {
    classes: object.isRequired,
    open: bool.isRequired,
    onClose: func.isRequired,
    totalCount: number,
    typeCounts: arrayOf(
        shape({
            type: string.isRequired,
            count: number.isRequired,
        }),
    ),
    publicContributors: arrayOf(
        shape({
            id: number,
            contributor_name: string,
            contributor_type: string,
            is_verified: bool,
            list_names: arrayOf(string),
        }),
    ),
    nonPublicContributors: arrayOf(
        shape({
            contributor_type: string,
            count: number,
        }),
    ),
};

SupplyChainNetworkDrawer.defaultProps = {
    totalCount: 0,
    typeCounts: [],
    publicContributors: [],
    nonPublicContributors: [],
};

export default withStyles(supplyChainNetworkDrawerStyles)(
    SupplyChainNetworkDrawer,
);
