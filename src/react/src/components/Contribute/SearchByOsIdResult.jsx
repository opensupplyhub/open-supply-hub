import React, { useEffect } from 'react';
import { useHistory, useParams, useLocation } from 'react-router-dom';
import { connect } from 'react-redux';
import isEmpty from 'lodash/isEmpty';
import { object, bool, func } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

import RequireAuthNotice from '../RequireAuthNotice';

import {
    fetchProductionLocationByOsId,
    resetSingleProductionLocation,
} from '../../actions/contributeProductionLocation';
import { contributeProductionLocationRoute } from '../../util/constants';
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
    const location = useLocation();
    const { osID } = useParams();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [location]);

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
        return <RequireAuthNotice title={TITLE} />;
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
