import React, { useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { connect } from 'react-redux';
import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import { object, bool, func } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

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
}) => {
    const location = useLocation();
    const history = useHistory();

    useEffect(() => {
        const osId = new URLSearchParams(location.search).get('os_id');

        if (osId) {
            fetchProductionLocation(osId);
        }
    }, [location.search, fetchProductionLocation]);

    const locationData = get(data, 'data[0]', {});
    const isLocationDataAvailable = !isEmpty(locationData);
    const {
        name,
        os_id: osId,
        historical_os_id: historicalOsIds,
        address,
        country: { name: countryName } = {},
    } = locationData;

    const handleBackToSearchByNameAddress = () => {
        clearProductionLocation();
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
    };

    const handleBackToSearchByOsId = () => {
        clearProductionLocation();
        history.push(`${contributeProductionLocationRoute}?tab=os-id`);
    };

    if (fetching) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    return (
        <div className={classes.mainContainerStyles}>
            <BackToSearchButton
                label="Back to ID search"
                handleBackToSearch={handleBackToSearchByOsId}
            />
            <Typography component="h1" className={classes.mainTitleStyles}>
                Production Location Search
            </Typography>

            <Paper className={classes.resultContainerStyles}>
                {isLocationDataAvailable ? (
                    <SearchByOsIdSuccessResult
                        name={name}
                        osId={osId}
                        historicalOsIds={historicalOsIds}
                        address={address}
                        countryName={countryName}
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

SearchByOsIdResult.defaultProps = {
    data: {},
    fetching: false,
};

SearchByOsIdResult.propTypes = {
    data: productionLocationPropType,
    fetching: bool,
    fetchProductionLocation: func.isRequired,
    clearProductionLocation: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        singleProductionLocation: { data, fetching },
    },
}) => ({
    data,
    fetching,
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
