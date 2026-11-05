import React from 'react';
import { bool, object, string } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import bannerStyles from '../../util/bannerStyles';
import COLOURS from '../../util/COLOURS';

const announcementBannerStyles = theme => {
    const base = bannerStyles(theme);
    return {
        ...base,
        body: {
            ...base.body,
            '& p': {
                margin: 0,
            },
            '& a': {
                color: COLOURS.PURPLE,
            },
        },
    };
};

const AnnouncementBanner = ({ isActive, content, classes }) => {
    if (!isActive || !content) {
        return null;
    }

    return (
        <div
            // The map and sidebar derive their height by subtracting every
            // header-height-contributor, so the banner must be counted.
            className={`header-height-contributor ${classes.banner}`}
            data-testid="announcement-banner"
        >
            <Typography
                component="div"
                variant="body1"
                className={classes.body}
                // The content is authored by Django admins in CKEditor.
                dangerouslySetInnerHTML={{ __html: content }}
            />
        </div>
    );
};

AnnouncementBanner.propTypes = {
    isActive: bool.isRequired,
    content: string.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({ announcementBanner: { banner } }) => ({
    isActive: !!banner.is_active,
    content: banner.content || '',
});

export default connect(mapStateToProps)(
    withStyles(announcementBannerStyles)(AnnouncementBanner),
);
