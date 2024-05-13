import React, { Component, Fragment } from 'react';
import { Route } from 'react-router-dom';
import { connect } from 'react-redux';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core';
import { userPropType } from '../util/propTypes';

import SidebarWithErrorBoundary from './SidebarWithErrorBoundary';
import FacilitiesMap from './FacilitiesMap';
import FacilitiesMapErrorMessage from './FacilitiesMapErrorMessage';
import FeatureFlag from './FeatureFlag';
import VectorTileFacilitiesMap from './VectorTileFacilitiesMap';

import '../styles/css/Map.css';

import withQueryStringSync from '../util/withQueryStringSync';

import { logErrorToRollbar } from './../util/util';
import { VECTOR_TILE, USER_DEFAULT_STATE } from '../util/constants';

const homepageStyles = theme =>
    Object.freeze({
        mapSidebarContainer: Object.freeze({
            [theme.breakpoints.down('md')]: {
                height: 'auto !important',
            },
        }),
    });

class Homepage extends Component {
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
        const { classes } = this.props;

        return (
            <Fragment>
                <Grid
                    container
                    className={`map-sidebar-container ${classes.mapSidebarContainer}`}
                >
                    <Grid item sm={12} md={6} id="sidebar-container">
                        <Route component={SidebarWithErrorBoundary} />
                    </Grid>
                    <Grid
                        item
                        sm={12}
                        md={6}
                        style={{ position: 'relative' }}
                        className="map-container"
                    >
                        {!hasError && (
                            <FeatureFlag
                                flag={VECTOR_TILE}
                                alternative={
                                    <Route component={FacilitiesMap} />
                                }
                            >
                                <Route component={VectorTileFacilitiesMap} />
                            </FeatureFlag>
                        )}
                        {hasError && <FacilitiesMapErrorMessage />}
                    </Grid>
                </Grid>
            </Fragment>
        );
    }
}

Homepage.propTypes = {
    user: userPropType,
};

Homepage.defaultProps = {
    user: USER_DEFAULT_STATE,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
}) {
    return { user };
}

export default connect(mapStateToProps)(
    withStyles(homepageStyles)(withQueryStringSync(Homepage)),
);
