import React from 'react';
import { connect } from 'react-redux';
import { Route, Switch, Redirect } from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';

import FeatureFlag from './FeatureFlag';
import FacilityDetails from './FacilityDetails';
import ProductionLocationDetailsContainer from './ProductionLocation/ProductionLocationDetailsContainer/ProductionLocationDetailsContainer';
import MapAndSidebar from './MapAndSidebar';

import withQueryStringSync from '../util/withQueryStringSync';
import {
    facilitiesRoute,
    facilityDetailsRoute,
    profileRoute,
    ENABLE_PRODUCTION_LOCATION_PAGE,
} from '../util/constants';

import { getFilteredSearchForEmbed, getLastPathParameter } from '../util/util';
import { embedUsesProductionLocationPage } from '../util/embeddedMap';
import UserProfile from './UserProfile';

const Facilities = ({
    fetchingFeatureFlags,
    isEmbedded,
    usesProductionLocationPage,
}) => {
    if (fetchingFeatureFlags) {
        return <CircularProgress />;
    }

    return (
        <Switch>
            <Route
                path={facilityDetailsRoute}
                render={props => {
                    const { location } = props;

                    const filteredSearch = getFilteredSearchForEmbed(
                        location.search,
                    );
                    const cleanOsID = getLastPathParameter(
                        location?.pathname || '',
                    );

                    // An embedded map shows a location at this address: on
                    // the production location page in its embed form while
                    // that switch is on, otherwise on the older details view.
                    if (isEmbedded) {
                        return usesProductionLocationPage ? (
                            <ProductionLocationDetailsContainer {...props} />
                        ) : (
                            <FacilityDetails {...props} />
                        );
                    }

                    return (
                        <FeatureFlag
                            flag={ENABLE_PRODUCTION_LOCATION_PAGE}
                            alternative={<FacilityDetails {...props} />}
                        >
                            <Redirect
                                to={{
                                    pathname: `/production-locations/${cleanOsID}`,
                                    search: filteredSearch,
                                }}
                            />
                        </FeatureFlag>
                    );
                }}
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

function mapStateToProps({ featureFlags, embeddedMap: { embed } }) {
    return {
        fetchingFeatureFlags: featureFlags.fetching,
        isEmbedded: !!embed,
        usesProductionLocationPage: embedUsesProductionLocationPage(
            embed,
            featureFlags,
        ),
    };
}

export default connect(mapStateToProps)(withQueryStringSync(Facilities));
