import React from 'react';
import {
    object,
    string,
    oneOfType,
    instanceOf,
    bool,
    number,
    node,
} from 'prop-types';
import { Link } from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import ScheduleIcon from '@material-ui/icons/Schedule';

import { makeProfileRouteLink, formatDate } from '../../../../util/util';
import { DATE_FORMATS } from '../../../../util/constants';
import {
    GA_LINK_PLACEMENT,
    sendLocationPartnerProfileLinkClick,
} from '../../../../util/analytics/gaCustomEvents';
import useViewerUserIdForAnalytics from '../../../../util/analytics/hooks';
import contributionCardStyles from './styles';

const ContributionCard = ({
    classes,
    value,
    sourceName,
    date,
    promoted,
    userId,
    spotlightGaProfileBase,
    'data-testid': dataTestId,
}) => {
    const viewerUserId = useViewerUserIdForAnalytics();
    const profilePath = makeProfileRouteLink(userId);

    const handleProfileClick = () => {
        if (!spotlightGaProfileBase || userId == null || !sourceName) {
            return;
        }
        const destinationUrl =
            typeof window !== 'undefined'
                ? `${window.location.origin}${profilePath}`
                : profilePath;
        sendLocationPartnerProfileLinkClick({
            contributorName: sourceName,
            partnerGroup: spotlightGaProfileBase.partner_group,
            linkPlacement: GA_LINK_PLACEMENT.CONTRIBUTIONS_DRAWER,
            destinationUrl,
            osId: spotlightGaProfileBase.os_id,
            partnerFieldName: spotlightGaProfileBase.partner_field_name,
            userId: String(userId),
            viewerUserId,
        });
    };

    return (
        <div
            className={
                promoted
                    ? `${classes.contributionCard} ${classes.contributionCardPromoted}`
                    : classes.contributionCard
            }
            data-testid={dataTestId}
        >
            <Typography
                component="div"
                className={
                    promoted
                        ? `${classes.contributionValue} ${classes.contributionValuePromoted}`
                        : classes.contributionValue
                }
            >
                {value}
            </Typography>
            <div className={classes.contributionValueContainer}>
                <div className={classes.contributionSourceContainer}>
                    {sourceName &&
                        (userId != null ? (
                            <Link
                                to={profilePath}
                                className={
                                    promoted
                                        ? `${classes.contributionSourceLink} ${classes.contributionSourceLinkPromoted}`
                                        : classes.contributionSourceLink
                                }
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={handleProfileClick}
                            >
                                {sourceName}
                            </Link>
                        ) : (
                            <Typography
                                className={
                                    promoted
                                        ? `${classes.contributionSource} ${classes.contributionSourcePromoted}`
                                        : classes.contributionSource
                                }
                            >
                                {sourceName}
                            </Typography>
                        ))}
                </div>
                <div className={classes.contributionMetaContainer}>
                    {date ? (
                        <span
                            className={
                                promoted
                                    ? `${classes.dateWithIcon} ${classes.dateWithIconPromoted}`
                                    : classes.dateWithIcon
                            }
                        >
                            <ScheduleIcon
                                fontSize="small"
                                className={
                                    promoted
                                        ? `${classes.dateIcon} ${classes.dateIconPromoted}`
                                        : classes.dateIcon
                                }
                            />
                            {formatDate(date, DATE_FORMATS.LONG)}
                        </span>
                    ) : null}
                </div>
            </div>
        </div>
    );
};

ContributionCard.propTypes = {
    classes: object.isRequired,
    value: oneOfType([string, node]).isRequired,
    sourceName: string,
    date: oneOfType([string, instanceOf(Date)]),
    promoted: bool,
    userId: oneOfType([string, number]),
    'data-testid': string,
    spotlightGaProfileBase: object,
};

ContributionCard.defaultProps = {
    sourceName: null,
    date: null,
    promoted: false,
    userId: null,
    'data-testid': undefined,
    spotlightGaProfileBase: null,
};

export default withStyles(contributionCardStyles)(ContributionCard);
