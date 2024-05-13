import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Route, Switch } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import { userPropType } from '../util/propTypes';

import FacilitiesMap from './FacilitiesMap';
import FacilitiesMapErrorMessage from './FacilitiesMapErrorMessage';
import FeatureFlag from './FeatureFlag';
import VectorTileFacilitiesMap from './VectorTileFacilitiesMap';

import '../styles/css/Map.css';

import { logErrorToRollbar } from './../util/util';
import {
    facilitiesRoute,
    facilityDetailsRoute,
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

Map.propTypes = {
    user: userPropType,
};

Map.defaultProps = {
    user: USER_DEFAULT_STATE,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
}) {
    return { user };
}

export default connect(mapStateToProps)(Map);
