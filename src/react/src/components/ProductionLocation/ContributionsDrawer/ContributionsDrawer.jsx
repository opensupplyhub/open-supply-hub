import React from 'react';
import {
    object,
    bool,
    func,
    string,
    node,
    shape,
    oneOfType,
    instanceOf,
    arrayOf,
    number,
} from 'prop-types';
import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';
import Divider from '@material-ui/core/Divider';
import CloseIcon from '@material-ui/icons/Close';
import PeopleOutlineIcon from '@material-ui/icons/PeopleOutline';

import ContributionCard from './ContributionCard';
import InfoBox from './InfoBox';
import styles from './styles';

const DEFAULT_TITLE = 'All Data Sources';
const PROMOTED_SECTION_LABEL = 'Highlighted Data Source';
const CONTRIBUTIONS_SECTION_LABEL = 'Other Data Sources';
const INFO_PROMOTED_TITLE = 'Why is this data source displayed first?';
const getInfoPromotedText = classes => (
    <>
        OS Hub automatically prioritizes data in this order: (1) claimed
        locations where owners/managers submitted data, (2) most frequently
        submitted values. The OS Hub team also actively moderates to promote
        quality data. To request reordering, email Support with the OS ID,
        preferred data entry, and justification.{' '}
        <a
            href="mailto:support@opensupplyhub.org"
            target="_blank"
            rel="noopener noreferrer"
            className={classes.supportLink}
        >
            Support
        </a>{' '}
        with the OS ID, preferred data entry, and justification.
    </>
);
const INFO_CONTRIBUTIONS_TEXT =
    'Multiple organizations may have shared information for this data point. You can see the list of historical data sources below. Click on the organization name to learn more about them and the data they have shared';
const LEARN_MORE_LABEL = 'Learn more about our open data model';
const LEARN_MORE_OPEN_DATA_MODEL_URL =
    'https://info.opensupplyhub.org/resources/an-open-data-model';

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
                        <PeopleOutlineIcon className={classes.titleIcon} />
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
                <Divider height={1} />
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
                            {infoPromotedText || getInfoPromotedText(classes)}
                        </InfoBox>
                        <ContributionCard
                            value={promotedContribution.value}
                            sourceName={promotedContribution.sourceName}
                            date={promotedContribution.date}
                            promoted
                        />
                    </>
                ) : null}

                <Typography className={classes.sectionLabel} component="p">
                    {sectionLabel}
                </Typography>
                <InfoBox
                    title={null}
                    variant="contributions"
                    learnMoreUrl={LEARN_MORE_OPEN_DATA_MODEL_URL}
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
                            />
                        ))}
                    </div>
                ) : null}
            </div>
        </Drawer>
    );
};

ContributionsDrawer.propTypes = {
    classes: object.isRequired,
    open: bool.isRequired,
    onClose: func.isRequired,
    title: string,
    subtitle: node,
    promotedContribution: shape({
        value: string,
        sourceName: string,
        date: oneOfType([string, instanceOf(Date)]),
        linkUrl: string,
    }),
    contributions: arrayOf(
        shape({
            id: oneOfType([string, number]),
            value: string,
            sourceName: string,
            date: oneOfType([string, instanceOf(Date)]),
            linkUrl: string,
        }),
    ),
    infoPromotedTitle: string,
    infoPromotedText: string,
    infoContributionsText: string,
};

ContributionsDrawer.defaultProps = {
    title: DEFAULT_TITLE,
    subtitle: null,
    promotedContribution: null,
    contributions: [],
    infoPromotedTitle: null,
    infoPromotedText: null,
    infoContributionsText: null,
};

export default withStyles(styles)(ContributionsDrawer);
