import React, { useEffect } from 'react';
import { arrayOf, bool, func, object } from 'prop-types';
import { useLocation } from 'react-router-dom';
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
import RequireAuthNotice from '../RequireAuthNotice';
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
    userHasSignedIn,
    fetchingSessionSignIn,
}) => {
    const TITLE = 'Production Location Search';
    const location = useLocation();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [location]);

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
        return <RequireAuthNotice title={TITLE} />;
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
