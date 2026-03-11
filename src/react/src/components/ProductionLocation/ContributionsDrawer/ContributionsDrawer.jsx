import React, { useMemo } from 'react';
import {
    object,
    bool,
    func,
    string,
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

import ContributionCard from './ContributionCard/ContributionCard';
import InfoBox from './InfoBox/InfoBox';
import {
    DEFAULT_TITLE,
    PROMOTED_SECTION_LABEL,
    INFO_PROMOTED_TITLE,
    INFO_CONTRIBUTIONS_TEXT,
    LEARN_MORE_LABEL,
    LEARN_MORE_OPEN_DATA_MODEL_URL,
} from './constants';
import InfoPromotedText from './InfoPromotedText/InfoPromotedText';
import DrawerSubtitle from './DrawerSubtitle/DrawerSubtitle';
import {
    getContributorCount,
    getContributionsCount,
    getContributionsSectionLabel,
} from './utils';
import contributionsDrawerStyles from './styles';

const ContributionsDrawer = ({
    classes,
    open,
    onClose,
    fieldName,
    promotedContribution,
    contributions,
}) => {
    const contributionsCount = useMemo(
        () => getContributionsCount(contributions),
        [contributions],
    );
    const contributorCount = useMemo(
        () => getContributorCount([...contributions, promotedContribution]),
        [contributions, promotedContribution],
    );
    const sectionLabel = useMemo(
        () => getContributionsSectionLabel(contributions),
        [contributions],
    );

    return (
        <Drawer open={open} onClose={onClose} anchor="right">
            <div
                className={classes.drawerContent}
                data-testid="contributions-drawer"
            >
                <div className={classes.header}>
                    <div className={classes.headerLeft}>
                        <PeopleOutlineIcon className={classes.titleIcon} />
                        <Typography
                            className={classes.title}
                            component="h2"
                            data-testid="contributions-drawer-title"
                        >
                            {DEFAULT_TITLE}
                        </Typography>
                    </div>
                    <IconButton
                        className={classes.closeButton}
                        aria-label="Close"
                        onClick={onClose}
                        data-testid="contributions-drawer-close"
                    >
                        <CloseIcon />
                    </IconButton>
                </div>
                <DrawerSubtitle
                    fieldName={fieldName}
                    contributorCount={contributorCount}
                />
                <Divider />
                {promotedContribution ? (
                    <>
                        <Typography
                            className={classes.sectionLabel}
                            component="p"
                            variant="body1"
                        >
                            {PROMOTED_SECTION_LABEL}
                        </Typography>
                        <InfoBox title={INFO_PROMOTED_TITLE} variant="promoted">
                            <InfoPromotedText />
                        </InfoBox>
                        <ContributionCard
                            value={promotedContribution.value}
                            sourceName={promotedContribution.sourceName}
                            date={promotedContribution.date}
                            promoted
                            userId={promotedContribution.userId}
                            data-testid="contribution-card-promoted"
                        />
                    </>
                ) : null}

                <Typography
                    className={classes.sectionLabel}
                    component="p"
                    variant="body1"
                >
                    {sectionLabel}
                </Typography>
                <InfoBox
                    title={null}
                    variant="contributions"
                    learnMoreUrl={LEARN_MORE_OPEN_DATA_MODEL_URL}
                    learnMoreLabel={LEARN_MORE_LABEL}
                >
                    {INFO_CONTRIBUTIONS_TEXT}
                </InfoBox>
                {contributionsCount > 0 ? (
                    <div data-testid="contributions-drawer-list">
                        {contributions.map((item, index) => (
                            <ContributionCard
                                key={
                                    item.id ||
                                    `${item.value}-${item.sourceName}-${index}`
                                }
                                value={item.value}
                                sourceName={item.sourceName}
                                date={item.date}
                                userId={item.userId}
                                data-testid="contribution-card"
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
    fieldName: string,
    promotedContribution: shape({
        value: string,
        sourceName: string,
        date: oneOfType([string, instanceOf(Date)]),
        linkUrl: string,
        userId: oneOfType([string, number]),
    }),
    contributions: arrayOf(
        shape({
            id: oneOfType([string, number]),
            value: string,
            sourceName: string,
            date: oneOfType([string, instanceOf(Date)]),
            linkUrl: string,
            userId: oneOfType([string, number]),
        }),
    ),
};

ContributionsDrawer.defaultProps = {
    fieldName: null,
    promotedContribution: null,
    contributions: [],
};

export default withStyles(contributionsDrawerStyles)(ContributionsDrawer);
