import React, { useEffect } from 'react';
import { arrayOf, bool, func, number, object } from 'prop-types';
import CircularProgress from '@material-ui/core/CircularProgress';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import {
    fetchProductionLocations,
    resetProductionLocations,
} from '../../actions/contributeProductionLocation';
import BackToSearchButton from './BackToSearchButton';
import SearchByNameAndAddressNotFoundResult from './SearchByNameAndAddressNotFoundResult';
import SearchByNameAndAddressSuccessResult from './SearchByNameAndAddressSuccessResult';
import { contributeProductionLocationRoute } from '../../util/constants';
import history from '../../util/history';
import { productionLocationPropType } from '../../util/propTypes';
import { makeSearchByNameAndAddressResultStyles } from '../../util/styles';

const SearchByNameAndAddressResult = ({
    data: productionLocations,
    count: productionLocationsCount,
    fetching,
    fetchLocations,
    clearLocations,
    classes,
}) => {
    useEffect(() => {
        fetchLocations();
    }, [fetchLocations]);

    const handleBackToSearchByNameAddress = () => {
        clearLocations();
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
    };

    if (fetching) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    return (
        <>
            <div className={classes.backToSearchButtonContainerStyles}>
                <BackToSearchButton
                    label="Back to Search"
                    handleBackToSearch={handleBackToSearchByNameAddress}
                />
            </div>
            {productionLocationsCount > 0 ? (
                <SearchByNameAndAddressSuccessResult
                    productionLocations={productionLocations}
                    productionLocationsCount={productionLocationsCount}
                    clearLocations={clearLocations}
                />
            ) : (
                <SearchByNameAndAddressNotFoundResult />
            )}
        </>
    );
};

SearchByNameAndAddressResult.propTypes = {
    data: arrayOf(productionLocationPropType).isRequired,
    count: number.isRequired,
    fetching: bool.isRequired,
    fetchLocations: func.isRequired,
    clearLocations: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        productionLocations: { data, count, fetching },
    },
}) => ({
    data,
    count,
    fetching,
});
const mapDispatchToProps = dispatch => ({
    fetchLocations: () => dispatch(fetchProductionLocations()),
    clearLocations: () => dispatch(resetProductionLocations()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(
    withStyles(makeSearchByNameAndAddressResultStyles)(
        SearchByNameAndAddressResult,
    ),
);
