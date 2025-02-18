import React, { useEffect } from 'react';
import { useHistory, useParams, Link } from 'react-router-dom';
import { connect } from 'react-redux';
import isEmpty from 'lodash/isEmpty';
import { object, bool, func } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

import AppGrid from '../AppGrid';

import {
    fetchProductionLocationByOsId,
    resetSingleProductionLocation,
} from '../../actions/contributeProductionLocation';
import {
    contributeProductionLocationRoute,
    authLoginFormRoute,
    LOG_IN_TITLE,
} from '../../util/constants';
import { makeSearchByOsIdResultStyles } from '../../util/styles';
import { productionLocationPropType } from '../../util/propTypes';

import BackToSearchButton from './BackToSearchButton';
import SearchByOsIdNotFoundResult from './SearchByOsIdNotFoundResult';
import SearchByOsIdSuccessResult from './SearchByOsIdSuccessResult';

const SearchByOsIdResult = ({
    data,
    fetching,
    fetchProductionLocation,
    clearProductionLocation,
    classes,
    userHasSignedIn,
    fetchingSessionSignIn,
}) => {
    const TITLE = 'Production Location Search';
    const history = useHistory();
    const { osID } = useParams();

    useEffect(() => {
        if (osID) {
            fetchProductionLocation(osID);
        }
    }, [osID, fetchProductionLocation]);

    const isLocationDataAvailable = !isEmpty(data);

    const handleBackToSearchByNameAddress = () => {
        clearProductionLocation();
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
    };

    const handleBackToSearchByOsId = () => {
        clearProductionLocation();
        history.push(`${contributeProductionLocationRoute}?tab=os-id`);
    };

    if (fetching || fetchingSessionSignIn) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    if (!userHasSignedIn) {
        return (
            <AppGrid title={TITLE}>
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <Link to={authLoginFormRoute} href={authLoginFormRoute}>
                            {LOG_IN_TITLE}
                        </Link>
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    return (
        <div className={classes.mainContainerStyles}>
            <BackToSearchButton
                label="Back to ID search"
                handleBackToSearch={handleBackToSearchByOsId}
            />
            <Typography component="h1" className={classes.mainTitleStyles}>
                {TITLE}
            </Typography>

            <Paper className={classes.resultContainerStyles}>
                {isLocationDataAvailable ? (
                    <SearchByOsIdSuccessResult
                        productionLocation={data}
                        handleBackToSearchByNameAddress={
                            handleBackToSearchByNameAddress
                        }
                    />
                ) : (
                    <SearchByOsIdNotFoundResult
                        handleBackToSearchByNameAddress={
                            handleBackToSearchByNameAddress
                        }
                        handleBackToSearchByOsId={handleBackToSearchByOsId}
                    />
                )}
            </Paper>
        </div>
    );
};

SearchByOsIdResult.propTypes = {
    data: productionLocationPropType.isRequired,
    fetching: bool.isRequired,
    fetchProductionLocation: func.isRequired,
    clearProductionLocation: func.isRequired,
    classes: object.isRequired,
    userHasSignedIn: bool.isRequired,
    fetchingSessionSignIn: bool.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        singleProductionLocation: { data, fetching },
    },
    auth: {
        user: { user },
        session: { fetching: fetchingSessionSignIn },
    },
}) => ({
    data,
    fetching,
    userHasSignedIn: !user.isAnon,
    fetchingSessionSignIn,
});

const mapDispatchToProps = dispatch => ({
    fetchProductionLocation: osId =>
        dispatch(fetchProductionLocationByOsId(osId)),
    clearProductionLocation: () => dispatch(resetSingleProductionLocation()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeSearchByOsIdResultStyles)(SearchByOsIdResult));
