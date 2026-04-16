import React from 'react';
import PropTypes from 'prop-types';
import { bool } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import COLOURS from '../../util/COLOURS';
import { DISABLE_LIST_UPLOADING } from '../../util/constants';

const styles = theme => ({
    banner: {
        width: '100%',
        boxSizing: 'border-box',
        backgroundColor: COLOURS.NAVIGATION,
        color: COLOURS.JET_BLACK,
        textAlign: 'center',
        padding: '12px 16px',
        [theme.breakpoints.down('sm')]: {
            padding: '8px 12px',
        },
    },
    headline: {
        fontSize: '21px',
        fontWeight: 600,
        lineHeight: 1.3,
        [theme.breakpoints.down('sm')]: {
            fontSize: '17px',
        },
    },
    body: {
        fontSize: '1rem',
        lineHeight: 1.4,
        [theme.breakpoints.down('sm')]: {
            fontSize: '0.875rem',
        },
    },
});

function MaintenanceBanner({ isActive, classes }) {
    if (!isActive) {
        return null;
    }

    return (
        <div className={classes.banner}>
            <Typography className={classes.headline} component="p">
                Open Supply Hub is currently undergoing planned maintenance.
            </Typography>
            <Typography className={classes.body} component="p">
                You can still search and browse, but data uploads are
                temporarily unavailable.
            </Typography>
            <Typography className={classes.body} component="p">
                Full service will resume shortly. Thank you for your patience.
            </Typography>
        </div>
    );
}

MaintenanceBanner.propTypes = {
    isActive: bool.isRequired,
    classes: PropTypes.object.isRequired,
};

function mapStateToProps({ featureFlags: { flags } }) {
    return {
        isActive: !!flags[DISABLE_LIST_UPLOADING],
    };
}

export default connect(mapStateToProps)(withStyles(styles)(MaintenanceBanner));
