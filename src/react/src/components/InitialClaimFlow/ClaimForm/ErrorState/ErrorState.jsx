import React from 'react';
import { func, object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

import errorStateStyles from './styles';

const ErrorState = ({ classes, error, onRetry }) => (
    <div className={classes.container}>
        <Paper className={classes.paper}>
            <div className={classes.errorContainer}>
                <Typography variant="title" className={classes.errorText}>
                    An error occurred while loading the claim form
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    {error}
                </Typography>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={onRetry}
                    className={classes.errorButton}
                >
                    Try Again
                </Button>
            </div>
        </Paper>
    </div>
);

ErrorState.propTypes = {
    classes: object.isRequired,
    error: string.isRequired,
    onRetry: func.isRequired,
};

export default withStyles(errorStateStyles)(ErrorState);
