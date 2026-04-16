import React from 'react';
import { bool, object } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import COLOURS from '../../util/COLOURS';
import { DISABLE_LIST_UPLOADING } from '../../util/constants';
import getTypographyStyles from '../../util/typographyStyles';

const styles = theme => {
    const typography = getTypographyStyles(theme);
    return {
        banner: {
            width: '100%',
            boxSizing: 'border-box',
            backgroundColor: COLOURS.NAVIGATION,
            textAlign: 'center',
            padding: '12px 16px',
            [theme.breakpoints.down('sm')]: {
                padding: '8px 12px',
            },
        },
        headline: {
            ...typography.formLabelTight,
            color: COLOURS.PURPLE,
            marginBottom: '15px',
            [theme.breakpoints.down('sm')]: {
                fontSize: typography.bodyText.fontSize,
                marginBottom: 0,
            },
        },
        body: {
            ...typography.sectionDescription,
            color: COLOURS.JET_BLACK,
            fontWeight: theme.typography.fontWeightBold,
            marginBottom: 0,
        },
    };
};

function MaintenanceBanner({ isActive, classes }) {
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
                Open Supply Hub is currently undergoing planned maintenance.
            </Typography>
            <Typography component="p" variant="body1" className={classes.body}>
                You can still search and browse, but data uploads are
                temporarily unavailable.
            </Typography>
            <Typography component="p" variant="body1" className={classes.body}>
                Full service will resume shortly. Thank you for your patience.
            </Typography>
        </div>
    );
}

MaintenanceBanner.propTypes = {
    isActive: bool.isRequired,
    classes: object.isRequired,
};

function mapStateToProps({ featureFlags: { flags } }) {
    return {
        isActive: !!flags[DISABLE_LIST_UPLOADING],
    };
}

export default connect(mapStateToProps)(withStyles(styles)(MaintenanceBanner));
