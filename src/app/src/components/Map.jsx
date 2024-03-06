import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';

import FacilitiesMap from './FacilitiesMap';
import FacilitiesMapErrorMessage from './FacilitiesMapErrorMessage';
import FeatureFlag from './FeatureFlag';
import VectorTileFacilitiesMap from './VectorTileFacilitiesMap';

import '../styles/css/Map.css';

import {
    facilitiesRoute,
    facilityDetailsRoute,
    VECTOR_TILE,
} from '../util/constants';

class Map extends Component {
    state = { hasError: false };

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error) {
        if (window.Rollbar) {
            window.Rollbar.error(error);
        }
    }

    render() {
        const { hasError } = this.state;
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
                            render={() => (
                                <FeatureFlag
                                    flag={VECTOR_TILE}
                                    alternative={
                                        <Route
                                            render={props => (
                                                <FacilitiesMap
                                                    {...props}
                                                    disableZoom
                                                />
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
                            )}
                        />
                        <Route
                            exact
                            path={facilitiesRoute}
                            render={() => (
                                <FeatureFlag
                                    flag={VECTOR_TILE}
                                    alternative={
                                        <Route component={FacilitiesMap} />
                                    }
                                >
                                    <Route
                                        component={VectorTileFacilitiesMap}
                                    />
                                </FeatureFlag>
                            )}
                        />
                    </Switch>
                )}
                {hasError && <FacilitiesMapErrorMessage />}
            </Grid>
        );
    }
}

export default Map;
