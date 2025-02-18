import React, { useEffect } from 'react';
import { arrayOf, bool, func, object } from 'prop-types';
import { useLocation, Link } from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Grid from '@material-ui/core/Grid';
import AppGrid from '../AppGrid';
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
    authLoginFormRoute,
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
    userHasSignedIn,
    fetchingSessionSignIn,
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

    if (fetching || fetchingSessionSignIn) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }
    if (!userHasSignedIn) {
        return (
            <AppGrid title="Contribute">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <Link to={authLoginFormRoute} href={authLoginFormRoute}>
                            Log in to contribute to Open Supply Hub
                        </Link>
                    </Grid>
                </Grid>
            </AppGrid>
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
    userHasSignedIn: bool.isRequired,
    fetchingSessionSignIn: bool.isRequired,
};

const mapStateToProps = ({
    auth: {
        user: { user },
        session: { fetching: fetchingSessionSignIn },
    },
    contributeProductionLocation: {
        productionLocations: { data, fetching },
    },
}) => ({
    data,
    fetching,
    userHasSignedIn: !user.isAnon,
    fetchingSessionSignIn,
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
