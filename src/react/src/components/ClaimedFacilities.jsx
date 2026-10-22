import React from 'react';
import { Switch, Route } from 'react-router-dom';

import ClaimedFacilitiesList from './ClaimedFacilitiesList';
import ClaimedFacilitiesDetails from './ClaimedFacilitiesDetails/ClaimedFacilitiesDetails';
import PendingClaimEdit from './PendingClaimEdit/PendingClaimEdit';
import RouteNotFound from './RouteNotFound';

import {
    claimedFacilitiesRoute,
    claimedFacilitiesDetailRoute,
    pendingClaimEditRoute,
} from '../util/constants';

export default function ClaimedFacilities() {
    return (
        <Switch>
            {/*
                Registered before the :claimID detail route so 'pending'
                is never captured as a claim id.
            */}
            <Route
                exact
                path={pendingClaimEditRoute}
                component={PendingClaimEdit}
            />
            <Route
                exact
                path={claimedFacilitiesDetailRoute}
                component={ClaimedFacilitiesDetails}
            />
            <Route
                exact
                path={claimedFacilitiesRoute}
                component={ClaimedFacilitiesList}
            />
            <Route render={() => <RouteNotFound />} />
        </Switch>
    );
}
