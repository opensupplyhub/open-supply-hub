import React from 'react';
import { connect } from 'react-redux';
import { Route, Switch, Redirect } from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';

import FeatureFlag from './FeatureFlag';
import FacilityDetails from './FacilityDetails';
import ProductionLocationDetails from './ProductionLocation/ProductionLocationDetails';
import MapAndSidebar from './MapAndSidebar';

import withQueryStringSync from '../util/withQueryStringSync';
import {
    facilitiesRoute,
    facilityDetailsRoute,
    productionLocationDetailsRoute,
    profileRoute,
    ENABLE_PRODUCTION_LOCATION_PAGE,
} from '../util/constants';
import UserProfile from './UserProfile';

const Facilities = ({ fetchingFeatureFlags }) => {
    if (fetchingFeatureFlags) {
        return <CircularProgress />;
    }

    return (
        <Switch>
            <Route path={facilityDetailsRoute} component={FacilityDetails} />
            <Route
                path={facilityDetailsRoute}
                render={() => (
                    <FeatureFlag
                        flag={ENABLE_PRODUCTION_LOCATION_PAGE}
                        alternative={FacilityDetails}
                    >
                        <Redirect
                            to={productionLocationDetailsRoute}
                            component={ProductionLocationDetails}
                        />
                    </FeatureFlag>
                )}
            />
            <Route path={facilitiesRoute} component={MapAndSidebar} />
            <Route
                path={profileRoute}
                component={({
                    match: {
                        params: { id },
                    },
                }) => <UserProfile id={id} />}
            />
        </Switch>
    );
};

function mapStateToProps({ featureFlags: { fetching: fetchingFeatureFlags } }) {
    return { fetchingFeatureFlags };
}

export default connect(mapStateToProps)(withQueryStringSync(Facilities));
