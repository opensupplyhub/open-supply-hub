import React, { useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { connect } from 'react-redux';
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
