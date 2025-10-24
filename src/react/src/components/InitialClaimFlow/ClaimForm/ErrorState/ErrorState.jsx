import React from 'react';
import { withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { func, object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';

import { mainRoute } from '../../../../util/constants';
import { resetClaimForm } from '../../../../actions/claimForm';
import { resetFilterOptions } from '../../../../actions/filterOptions';
import { resetSingleProductionLocation } from '../../../../actions/contributeProductionLocation';
import errorStateStyles from './styles';
import withScrollReset from '../../HOCs/withScrollReset';

const ErrorState = ({
    classes,
    error,
    onRetry,
    resetForm,
    resetFilters,
    resetProductionLocation,
    history,
}) => {
    const handleGoToMainPage = () => {
        resetForm();
        resetFilters();
        resetProductionLocation();
        history.push(mainRoute);
    };

    return (
        <div className={classes.container}>
            <Paper className={classes.paper}>
                <div className={classes.errorContainer}>
                    <Typography variant="title" className={classes.errorTitle}>
                        An error occurred while loading the claim form.
                    </Typography>
                    <Typography
                        variant="subheading"
                        color="textSecondary"
                        className={classes.errorText}
                    >
                        {error} If the issue continues, feel free to contact our
                        support team.
                    </Typography>
                    <Grid container className={classes.buttonContainer}>
                        <Grid item>
                            <Button
                                variant="contained"
                                className={classes.searchButton}
                                onClick={handleGoToMainPage}
                            >
                                Search OS Hub
                            </Button>
                        </Grid>
                        <Grid item>
                            <Button
                                variant="outlined"
                                onClick={onRetry}
                                className={classes.errorButton}
                            >
                                Try Again
                            </Button>
                        </Grid>
                    </Grid>
                </div>
            </Paper>
        </div>
    );
};

ErrorState.propTypes = {
    classes: object.isRequired,
    error: string.isRequired,
    onRetry: func.isRequired,
    resetForm: func.isRequired,
    resetFilters: func.isRequired,
    resetProductionLocation: func.isRequired,
    history: object.isRequired,
};

const mapDispatchToProps = dispatch => ({
    resetForm: () => dispatch(resetClaimForm()),
    resetFilters: () => dispatch(resetFilterOptions()),
    resetProductionLocation: () => dispatch(resetSingleProductionLocation()),
});

export default connect(
    null,
    mapDispatchToProps,
)(withRouter(withStyles(errorStateStyles)(withScrollReset(ErrorState))));
