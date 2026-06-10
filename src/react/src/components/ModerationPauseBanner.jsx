import React from 'react';
import { bool, object } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import { ENABLE_MODERATION_PAUSE_INFO } from '../util/constants';
import moderationPauseBannerStyles from '../util/bannerStyles';

const ModerationPauseBanner = ({ isActive, classes }) => {
    if (!isActive) {
        return null;
    }

    return (
        <div className={classes.banner}>
            <Typography
                component="p"
                variant="headline"
                className={classes.headline}
            >
                Planning to upload data soon? From Monday, June 29th to Friday,
                August 7th 2026, we are running an Automation Sprint and
                processing times will be extended.
            </Typography>
            <Typography component="p" variant="body1" className={classes.body}>
                List uploads, adding a single production location (OS ID), and
                claims submitted during this window will take at least 6
                additional weeks beyond our{' '}
                <a
                    href="https://info.opensupplyhub.org/resources/data-processing-timelines"
                    target="_blank"
                    rel="noreferrer"
                >
                    standard timelines
                </a>{' '}
                to go live.
            </Typography>
            <Typography component="p" variant="body1" className={classes.body}>
                If timing matters, we recommend submitting before June 29th.{' '}
                <a
                    href="https://info.opensupplyhub.org/resources/automation-sprint-2026"
                    target="_blank"
                    rel="noreferrer"
                >
                    Learn more.
                </a>
            </Typography>
        </div>
    );
};

ModerationPauseBanner.propTypes = {
    isActive: bool.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({ featureFlags: { flags } }) => ({
    isActive: !!flags[ENABLE_MODERATION_PAUSE_INFO],
});

export default connect(mapStateToProps)(
    withStyles(moderationPauseBannerStyles)(ModerationPauseBanner),
);
