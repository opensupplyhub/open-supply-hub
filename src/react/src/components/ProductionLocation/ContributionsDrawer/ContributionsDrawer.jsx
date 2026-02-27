import React from 'react';
import PropTypes from 'prop-types';
import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';

import CloseIcon from '@material-ui/icons/Close';
import GroupIcon from '@material-ui/icons/Group';

import ContributionCard from './ContributionCard';
import InfoBox from './InfoBox';
import styles from './styles';

const DEFAULT_TITLE = 'All Data Contributions';
const PROMOTED_SECTION_LABEL = 'PROMOTED CONTRIBUTION';
const CONTRIBUTIONS_SECTION_LABEL = 'CONTRIBUTIONS';
const INFO_PROMOTED_TITLE =
    'Why is this data displayed over other contributions?';
const INFO_PROMOTED_TEXT =
    'OS Hub prioritizes data from claimed production location owners and verified sources. When multiple entries exist, we display the most recently verified data from the highest-confidence source.';
const INFO_CONTRIBUTIONS_TEXT =
    'Multiple organizations may contribute data about the same production location. Each contributor uploads data via a named list — use list names to understand the context and source of the data.';
const LEARN_MORE_LABEL = 'Learn more about our open data model';

const ContributionsDrawer = ({
    classes,
    open,
    onClose,
    title,
    subtitle,
    promotedContribution,
    contributions,
    infoPromotedTitle,
    infoPromotedText,
    infoContributionsText,
    learnMoreUrl,
}) => {
    const contributionsCount = Array.isArray(contributions)
        ? contributions.length
        : 0;
    const sectionLabel =
        contributionsCount > 0
            ? `${CONTRIBUTIONS_SECTION_LABEL} (${contributionsCount})`
            : CONTRIBUTIONS_SECTION_LABEL;

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            classes={{ paper: classes.drawerPaper }}
        >
            <div className={classes.drawerContent}>
                <div className={classes.header}>
                    <div className={classes.headerLeft}>
                        <GroupIcon className={classes.titleIcon} />
                        <Typography className={classes.title} component="h2">
                            {title || DEFAULT_TITLE}
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
                {subtitle ? (
                    <Typography className={classes.subtitle} component="p">
                        {subtitle}
                    </Typography>
                ) : null}

                {promotedContribution ? (
                    <>
                        <Typography
                            className={classes.sectionLabel}
                            component="p"
                        >
                            {PROMOTED_SECTION_LABEL}
                        </Typography>
                        <InfoBox
                            title={infoPromotedTitle || INFO_PROMOTED_TITLE}
                            variant="promoted"
                        >
                            {infoPromotedText || INFO_PROMOTED_TEXT}
                        </InfoBox>
                        <ContributionCard
                            value={promotedContribution.value}
                            sourceName={promotedContribution.sourceName}
                            date={promotedContribution.date}
                            linkUrl={promotedContribution.linkUrl}
                        />
                    </>
                ) : null}

                <Typography className={classes.sectionLabel} component="p">
                    {sectionLabel}
                </Typography>
                <InfoBox
                    title={null}
                    variant="contributions"
                    learnMoreUrl={learnMoreUrl}
                    learnMoreLabel={LEARN_MORE_LABEL}
                >
                    {infoContributionsText || INFO_CONTRIBUTIONS_TEXT}
                </InfoBox>
                {contributionsCount > 0 ? (
                    <div className={classes.listScroll}>
                        {contributions.map((item, index) => (
                            <ContributionCard
                                key={
                                    item.id ||
                                    `${item.value}-${item.sourceName}-${index}`
                                }
                                value={item.value}
                                sourceName={item.sourceName}
                                date={item.date}
                                linkUrl={item.linkUrl}
                            />
                        ))}
                    </div>
                ) : null}
            </div>
        </Drawer>
    );
};

ContributionsDrawer.propTypes = {
    classes: PropTypes.object.isRequired,
    open: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    title: PropTypes.string,
    subtitle: PropTypes.node,
    promotedContribution: PropTypes.shape({
        value: PropTypes.string,
        sourceName: PropTypes.string,
        date: PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.instanceOf(Date),
        ]),
        linkUrl: PropTypes.string,
    }),
    contributions: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            value: PropTypes.string,
            sourceName: PropTypes.string,
            date: PropTypes.oneOfType([
                PropTypes.string,
                PropTypes.instanceOf(Date),
            ]),
            linkUrl: PropTypes.string,
        }),
    ),
    infoPromotedTitle: PropTypes.string,
    infoPromotedText: PropTypes.string,
    infoContributionsText: PropTypes.string,
    learnMoreUrl: PropTypes.string,
};

ContributionsDrawer.defaultProps = {
    title: DEFAULT_TITLE,
    subtitle: null,
    promotedContribution: null,
    contributions: [],
    infoPromotedTitle: null,
    infoPromotedText: null,
    infoContributionsText: null,
    learnMoreUrl: null,
};

export default withStyles(styles)(ContributionsDrawer);
