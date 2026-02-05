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

import '../styles/css/Map.css';

import {
    logErrorToRollbar,
    shouldUseProductionLocationPage,
} from './../util/util';
import {
    facilitiesRoute,
    facilityDetailsRoute,
    productionLocationDetailsRoute,
    VECTOR_TILE,
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
        const { useProductionLocationPage } = this.props;

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

        const renderFacilitiesRoute = () => (
            <FeatureFlag
                flag={VECTOR_TILE}
                alternative={<Route component={FacilitiesMap} />}
            >
                <Route component={VectorTileFacilitiesMap} />
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
                            render={props =>
                                useProductionLocationPage ? (
                                    <Redirect
                                        to={{
                                            pathname: productionLocationDetailsRoute.replace(
                                                ':osID',
                                                props.match.params.osID,
                                            ),
                                            search: props.location.search,
                                        }}
                                    />
                                ) : (
                                    renderDetailRoute()
                                )
                            }
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
};

Map.defaultProps = {
    user: USER_DEFAULT_STATE,
    useProductionLocationPage: false,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
    featureFlags,
}) {
    return {
        user,
        useProductionLocationPage: shouldUseProductionLocationPage(
            featureFlags,
        ),
    };
}

export default connect(mapStateToProps)(Map);
