import React, { Component } from 'react';
import { connect } from 'react-redux';
import { bool, func } from 'prop-types';
import { Router, Route, Switch } from 'react-router-dom';
import { ToastContainer, Slide } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'; // eslint-disable-line import/first
import CircularProgress from '@material-ui/core/CircularProgress';

import history from './util/history';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import EmbeddedFooter from './components/EmbeddedFooter';
import RegisterForm from './components/RegisterForm';
import ResetPasswordForm from './components/ResetPasswordForm';
import LoginForm from './components/LoginForm';
import ContributeList from './components/ContributeList';
import AddLocationData from './components/AddLocationData';
import Homepage from './components/Homepage';
import FacilityLists from './components/FacilityLists';
import FacilityListItems from './components/FacilityListItems';
import ErrorBoundary from './components/ErrorBoundary';
import GDPRNotification from './components/GDPRNotification';
import ConfirmRegistration from './components/ConfirmRegistration';
import RouteNotFound from './components/RouteNotFound';
import Dashboard from './components/Dashboard';
import FeatureFlag from './components/FeatureFlag';
import ClaimFacility from './components/ClaimFacility';
import ClaimForm from './components/InitialClaimFlow/ClaimForm/ClaimForm';
import ClaimedFacilities from './components/ClaimedFacilities';
import SurveyDialogNotification from './components/SurveyDialogNotification';
import Settings from './components/Settings/Settings';
import ExternalRedirect from './components/ExternalRedirect';
import Facilities from './components/Facilities';
import ProductionLocationDetailsContainer from './components/ProductionLocation/ProductionLocationDetailsContainer';
import ContributeProductionLocation from './components/Contribute/ContributeProductionLocation';
import SearchByOsIdResult from './components/Contribute/SearchByOsIdResult';
import SearchByNameAndAddressResult from './components/Contribute/SearchByNameAndAddressResult';
import ProductionLocationInfo from './components/Contribute/ProductionLocationInfo';
import withProductionLocationSubmit from './components/Contribute/HOC/withProductionLocationSubmit';
import ClaimIntro from './components/InitialClaimFlow/ClaimIntro/ClaimIntro';

import { sessionLogin } from './actions/auth';
import { fetchFeatureFlags } from './actions/featureFlags';
import { reportWindowResize } from './actions/ui';

import { setFacilityGridRamp } from './actions/vectorTileLayer';

import {
    mainRoute,
    authLoginFormRoute,
    authRegisterFormRoute,
    authResetPasswordFormRoute,
    authConfirmRegistrationRoute,
    multipleLocationRoute,
    contributeRoute,
    listsRoute,
    facilityListItemsRoute,
    facilitiesRoute,
    productionLocationDetailsRoute,
    dashboardRoute,
    claimFacilityRoute,
    claimIntroRoute,
    claimDetailsRoute,
    claimedFacilitiesRoute,
    CLAIM_A_FACILITY,
    settingsRoute,
    InfoLink,
    InfoPaths,
    contributeProductionLocationRoute,
    searchByOsIdResultRoute,
    searchByNameAndAddressResultRoute,
    productionLocationInfoRouteCreate,
    productionLocationInfoRouteUpdate,
    ENABLE_PRODUCTION_LOCATION_PAGE,
} from './util/constants';

// Pre-wrapping components outside of Routes to prevent redundant re-renders on component mount
const WrappedProductionLocationInfoUpdate = withProductionLocationSubmit(
    ProductionLocationInfo,
);
const WrappedProductionLocationInfoCreate = withProductionLocationSubmit(
    ProductionLocationInfo,
);

class Routes extends Component {
    componentDidMount() {
        window.addEventListener('resize', () =>
            this.props.handleWindowResize({
                innerHeight: window.innerHeight,
                innerWidth: window.innerWidth,
            }),
        );

        window.setGridColorRamp = this.props.setRamp;
        this.props.getFeatureFlags();

        return this.props.logIn();
    }

    render() {
        const { fetchingFeatureFlags, embed } = this.props;

        const mainPanelStyle = embed ? { top: 0, bottom: '64px' } : {};

        return (
            <ErrorBoundary>
                <Router history={history}>
                    <div className="App">
                        {!embed ? <Navbar /> : null}
                        <main
                            style={mainPanelStyle}
                            className="mainPanel"
                            id="mainPanel"
                        >
                            <Switch>
                                <Route
                                    exact
                                    path={claimFacilityRoute}
                                    render={() => (
                                        <FeatureFlag
                                            flag={CLAIM_A_FACILITY}
                                            alternative={
                                                <Route component={Facilities} />
                                            }
                                        >
                                            <Route component={ClaimFacility} />
                                        </FeatureFlag>
                                    )}
                                />
                                <Route
                                    path={claimedFacilitiesRoute}
                                    render={() => (
                                        <FeatureFlag
                                            flag={CLAIM_A_FACILITY}
                                            alternative={<RouteNotFound />}
                                        >
                                            <Route
                                                component={ClaimedFacilities}
                                            />
                                        </FeatureFlag>
                                    )}
                                />
                                <Route
                                    exact
                                    path={claimIntroRoute}
                                    component={ClaimIntro}
                                />
                                <Route
                                    exact
                                    path={claimDetailsRoute}
                                    component={ClaimForm}
                                />
                                <Route
                                    path={facilitiesRoute}
                                    component={Facilities}
                                />
                                <Route
                                    path={productionLocationDetailsRoute}
                                    render={() => (
                                        <FeatureFlag
                                            flag={
                                                ENABLE_PRODUCTION_LOCATION_PAGE
                                            }
                                            alternative={<RouteNotFound />}
                                        >
                                            <Route
                                                component={
                                                    ProductionLocationDetailsContainer
                                                }
                                            />
                                        </FeatureFlag>
                                    )}
                                />
                                <Route
                                    exact
                                    path={authRegisterFormRoute}
                                    component={RegisterForm}
                                />
                                <Route
                                    exact
                                    path={authLoginFormRoute}
                                    component={LoginForm}
                                />
                                <Route
                                    exact
                                    path={authResetPasswordFormRoute}
                                    component={ResetPasswordForm}
                                />
                                <Route
                                    exact
                                    path={authConfirmRegistrationRoute}
                                    component={ConfirmRegistration}
                                />
                                <Route
                                    exact
                                    path={multipleLocationRoute}
                                    component={ContributeList}
                                />
                                <Route
                                    exact
                                    path={contributeRoute}
                                    component={AddLocationData}
                                />
                                <Route
                                    path={dashboardRoute}
                                    component={Dashboard}
                                />
                                <Route
                                    path={facilityListItemsRoute}
                                    component={FacilityListItems}
                                />
                                <Route
                                    path={listsRoute}
                                    component={FacilityLists}
                                />
                                <Route
                                    exact
                                    path={settingsRoute}
                                    component={Settings}
                                />
                                <Route
                                    exact
                                    path={contributeProductionLocationRoute}
                                    component={ContributeProductionLocation}
                                />
                                <Route
                                    exact
                                    path={searchByOsIdResultRoute}
                                    component={SearchByOsIdResult}
                                />
                                <Route
                                    exact
                                    path={searchByNameAndAddressResultRoute}
                                    component={SearchByNameAndAddressResult}
                                />
                                <Route
                                    exact
                                    path={productionLocationInfoRouteUpdate}
                                    component={
                                        WrappedProductionLocationInfoUpdate
                                    }
                                />
                                <Route
                                    exact
                                    path={productionLocationInfoRouteCreate}
                                    component={
                                        WrappedProductionLocationInfoCreate
                                    }
                                />
                                <Route exact path="/about/processing">
                                    <ExternalRedirect
                                        to={`${InfoLink}/${InfoPaths.dataQuality}`}
                                    />
                                </Route>
                                <Route exact path="/about/claimedfacilities">
                                    <ExternalRedirect
                                        to={`${InfoLink}/${InfoPaths.claimedFacilities}`}
                                    />
                                </Route>
                                <Route exact path="/tos">
                                    <ExternalRedirect
                                        to={`${InfoLink}/${InfoPaths.termsOfService}`}
                                    />
                                </Route>
                                <Route
                                    exact
                                    path={mainRoute}
                                    render={() => {
                                        if (fetchingFeatureFlags) {
                                            return <CircularProgress />;
                                        }

                                        return <Route component={Homepage} />;
                                    }}
                                />
                                <Route
                                    path={mainRoute}
                                    component={Facilities}
                                />
                                <Route render={() => <RouteNotFound />} />
                            </Switch>
                        </main>
                        {embed ? <EmbeddedFooter /> : <Footer />}
                        <ToastContainer
                            position="bottom-center"
                            transition={Slide}
                        />
                        <GDPRNotification />
                        <SurveyDialogNotification />
                    </div>
                </Router>
            </ErrorBoundary>
        );
    }
}

Routes.propTypes = {
    logIn: func.isRequired,
    fetchingFeatureFlags: bool.isRequired,
};

function mapStateToProps({
    featureFlags: { fetching: fetchingFeatureFlags },
    embeddedMap: { embed },
    filters,
}) {
    return {
        fetchingFeatureFlags,
        embed: !!embed,
        contributor: filters?.contributors[0],
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getFeatureFlags: () => dispatch(fetchFeatureFlags()),
        logIn: () => dispatch(sessionLogin()),
        handleWindowResize: data => dispatch(reportWindowResize(data)),
        setRamp: ramp => dispatch(setFacilityGridRamp(ramp)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(Routes);
