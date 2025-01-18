import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { arrayOf, bool, func, object } from 'prop-types';
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
import {
    contributeProductionLocationRoute,
    MAX_LOCATIONS_TO_SHOW,
} from '../../util/constants';
import history from '../../util/history';
import { productionLocationPropType } from '../../util/propTypes';
import { makeSearchByNameAndAddressResultStyles } from '../../util/styles';

const SearchByNameAndAddressResult = ({
    data: productionLocations,
    fetching,
    fetchLocations,
    clearLocations,
    classes,
}) => {
    const location = useLocation();

    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);
        const name = searchParams.get('name');
        const address = searchParams.get('address');
        const country = searchParams.get('country');
        fetchLocations({ name, address, country, size: MAX_LOCATIONS_TO_SHOW });
    }, [location.search, fetchLocations]);

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
            {productionLocations.length > 0 ? (
                <SearchByNameAndAddressSuccessResult
                    productionLocations={productionLocations}
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
    fetching: bool.isRequired,
    fetchLocations: func.isRequired,
    clearLocations: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        productionLocations: { data, fetching },
    },
}) => ({
    data,
    count,
    fetching,
});
const mapDispatchToProps = dispatch => ({
    fetchLocations: data => dispatch(fetchProductionLocations(data)),
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
