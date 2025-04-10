import React from 'react';
import { func, object, node } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import { notificationContainerStyles } from './styles';

const NotificationContainer = ({ showNotification, children, classes }) => (
    <Grid
        container
        direction="row"
        alignItems="flex-start"
        className={classes.notificationWrapper}
    >
        <Grid item>
            <ErrorOutlineIcon className={classes.icon} />
        </Grid>
        <Grid item className={classes.errorContentWrapper}>
            {children}
        </Grid>
        <Grid item className={classes.closeButtonWrapper}>
            <IconButton
                aria-label="Close"
                onClick={() => showNotification(false)}
                className={classes.closeButton}
            >
                <CloseIcon className={classes.icon} />
            </IconButton>
        </Grid>
    </Grid>
);

NotificationContainer.propTypes = {
    showNotification: func.isRequired,
    children: node.isRequired,
    classes: object.isRequired,
};

export default withStyles(notificationContainerStyles)(NotificationContainer);
