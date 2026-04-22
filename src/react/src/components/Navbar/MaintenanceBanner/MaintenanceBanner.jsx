import React from 'react';
import { bool, object } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import { DISABLE_LIST_UPLOADING } from '../../../util/constants';
import styles from './styles';

const MaintenanceBanner = ({ isActive, classes }) => {
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
};

MaintenanceBanner.propTypes = {
    isActive: bool.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({ featureFlags: { flags } }) => ({
    isActive: !!flags[DISABLE_LIST_UPLOADING],
});

export default connect(mapStateToProps)(withStyles(styles)(MaintenanceBanner));
