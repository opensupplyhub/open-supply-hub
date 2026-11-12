import React, { Component } from 'react';
import { bool } from 'prop-types';
import { connect } from 'react-redux';
import { Redirect, Route, Switch } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import { userPropType } from '../util/propTypes';

import FacilitiesMap from './FacilitiesMap';
import FacilitiesMapErrorMessage from './FacilitiesMapErrorMessage';
import FeatureFlag from './FeatureFlag';
import VectorTileFacilitiesMap from './VectorTileFacilitiesMap';
import CountryMap from './CountryMap/CountryMap';

import '../styles/css/Map.css';

import {
    logErrorToRollbar,
    shouldUseProductionLocationPage,
    getFilteredSearchForEmbed,
    getLastPathParameter,
} from './../util/util';
import {
    facilitiesRoute,
    facilityDetailsRoute,
    productionLocationDetailsRoute,
    VECTOR_TILE,
    COUNTRY_MAP,
    USER_DEFAULT_STATE,
} from '../util/constants';

class Map extends Component {
    state = { hasError: false };

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error) {
        const { user } = this.props;
        logErrorToRollbar(window, error, user);
    }

    render() {
        const { hasError } = this.state;
        const { useProductionLocationPage, isEmbedded } = this.props;

        const renderDetailRoute = () => (
            <FeatureFlag
                flag={VECTOR_TILE}
                alternative={
                    <Route
                        render={props => (
                            <FacilitiesMap {...props} disableZoom />
                        )}
                    />
                }
            >
                <Route
                    render={props => (
                        <VectorTileFacilitiesMap
                            {...props}
                            disableZoom
                            disableZoomToSearch
                        />
                    )}
                />
            </FeatureFlag>
        );

        // The country map supersedes the tile map where its switch is on.
        // Falls through to the existing flag chain everywhere else, so the
        // search page is unchanged until the switch is flipped.
        const renderFacilitiesRoute = () => (
            <FeatureFlag
                flag={COUNTRY_MAP}
                alternative={
                    <FeatureFlag
                        flag={VECTOR_TILE}
                        alternative={<Route component={FacilitiesMap} />}
                    >
                        <Route component={VectorTileFacilitiesMap} />
                    </FeatureFlag>
                }
            >
                <Route
                    render={props => (
                        <CountryMap {...props} height={this.props.height} />
                    )}
                />
            </FeatureFlag>
        );

        return (
            <Grid
                item
                xs={12}
                sm={7}
                className="map-container"
                style={this.props.height ? { height: this.props.height } : {}}
            >
                {!hasError && (
                    <Switch>
                        <Route
                            exact
                            path={facilityDetailsRoute}
                            render={props => {
                                const filteredSearch = getFilteredSearchForEmbed(
                                    props.location.search,
                                );
                                const cleanOsID = getLastPathParameter(
                                    props.location?.pathname || '',
                                );

                                if (isEmbedded) {
                                    return renderDetailRoute();
                                }

                                if (useProductionLocationPage) {
                                    return (
                                        <Redirect
                                            to={{
                                                pathname: productionLocationDetailsRoute.replace(
                                                    ':osID',
                                                    cleanOsID,
                                                ),
                                                search: filteredSearch,
                                            }}
                                        />
                                    );
                                }

                                return renderDetailRoute();
                            }}
                        />
                        <Route
                            exact
                            path={productionLocationDetailsRoute}
                            render={() => renderDetailRoute()}
                        />
                        <Route
                            exact
                            path={facilitiesRoute}
                            render={() => renderFacilitiesRoute()}
                        />
                    </Switch>
                )}
                {hasError && <FacilitiesMapErrorMessage />}
            </Grid>
        );
    }
}

Map.propTypes = {
    user: userPropType,
    useProductionLocationPage: bool,
    isEmbedded: bool,
};

Map.defaultProps = {
    user: USER_DEFAULT_STATE,
    useProductionLocationPage: false,
    isEmbedded: false,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
    featureFlags,
    embeddedMap: { embed },
}) {
    return {
        user,
        useProductionLocationPage: shouldUseProductionLocationPage(
            featureFlags,
        ),
        isEmbedded: !!embed,
    };
}

export default connect(mapStateToProps)(Map);
