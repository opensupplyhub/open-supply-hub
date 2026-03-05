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
import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import { Link } from 'react-router-dom';

import { makeProfileRouteLink } from '../../../../../util/util';
import pluralizeContributorType from '../utils';
import {
    DRAWER_TITLE,
    ANONYMIZED_SECTION_TITLE,
    ALL_DATA_SOURCES_LABEL,
    INFO_TEXT,
    LEARN_MORE_LABEL,
    LEARN_MORE_URL,
    UPLOADED_VIA_LIST_LABEL,
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
}) => {
    const allSourcesLabel =
        totalCount > 0
            ? `${ALL_DATA_SOURCES_LABEL} (${totalCount})`
            : ALL_DATA_SOURCES_LABEL;

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            classes={{ paper: classes.drawerPaper }}
        >
            <div
                className={classes.drawerContent}
                data-testid="supply-chain-drawer"
            >
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
                        data-testid="supply-chain-drawer-close"
                    >
                        <CloseIcon />
                    </IconButton>
                </div>

                <Typography className={classes.subtitle} component="p">
                    {totalCount}{' '}
                    {totalCount === 1
                        ? 'organization has'
                        : 'organizations have'}{' '}
                    shared data about this production location
                </Typography>

                <Divider style={{ height: 1 }} />

                <Typography className={classes.sectionLabel} component="p">
                    {allSourcesLabel}
                </Typography>

                <div className={classes.infoBox}>
                    <div className={classes.infoBoxWithIcon}>
                        <InfoOutlinedIcon className={classes.infoIcon} />
                        <div className={classes.infoBoxContent}>
                            <Typography
                                className={classes.infoText}
                                component="div"
                            >
                                {INFO_TEXT}
                            </Typography>
                            <a
                                href={LEARN_MORE_URL}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={classes.learnMoreLink}
                            >
                                {LEARN_MORE_LABEL}
                                <span className={classes.learnMoreArrow}>
                                    →
                                </span>
                            </a>
                        </div>
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
                                <strong>{count}</strong>{' '}
                                {pluralizeContributorType(type, count)}
                            </Typography>
                        ))}
                    </div>
                )}

                <div className={classes.listScroll}>
                    {publicContributors.map(contributor => (
                        <div
                            key={contributor.id}
                            className={classes.contributorEntry}
                        >
                            <Link
                                to={makeProfileRouteLink(contributor.id)}
                                className={classes.contributorName}
                            >
                                {contributor.contributor_name}
                                <OpenInNewIcon
                                    className={classes.externalLinkIcon}
                                />
                            </Link>
                            {contributor.contributor_type && (
                                <Typography
                                    className={classes.contributorType}
                                    component="p"
                                >
                                    {contributor.contributor_type}
                                </Typography>
                            )}
                            {contributor.list_names &&
                                contributor.list_names.map(
                                    listName =>
                                        listName && (
                                            <div
                                                key={`${contributor.id}-${listName}`}
                                                className={classes.listEntry}
                                            >
                                                <Typography
                                                    className={
                                                        classes.listEntryLabel
                                                    }
                                                    component="p"
                                                >
                                                    <ListIcon
                                                        className={
                                                            classes.listIcon
                                                        }
                                                    />
                                                    {UPLOADED_VIA_LIST_LABEL}
                                                </Typography>
                                                <Typography
                                                    className={classes.listName}
                                                    component="p"
                                                >
                                                    {listName}
                                                </Typography>
                                            </div>
                                        ),
                                )}
                        </div>
                    ))}
                </div>

                {nonPublicContributors.length > 0 && (
                    <>
                        <Typography
                            className={classes.sectionLabel}
                            component="p"
                        >
                            {ANONYMIZED_SECTION_TITLE}
                        </Typography>
                        {nonPublicContributors.map(contributor => (
                            <Typography
                                key={contributor.contributor_type}
                                className={classes.anonymizedType}
                                component="p"
                            >
                                {contributor.count}{' '}
                                {pluralizeContributorType(
                                    contributor.contributor_type,
                                    contributor.count,
                                )}
                            </Typography>
                        ))}
                    </>
                )}
            </div>
        </Drawer>
    );
};

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
            id: number.isRequired,
            contributor_name: string,
            contributor_type: string,
            list_names: arrayOf(string),
        }),
    ),
    nonPublicContributors: arrayOf(
        shape({
            contributor_type: string.isRequired,
            count: number.isRequired,
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
