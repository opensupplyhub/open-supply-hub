import React, { Component } from 'react';
import { Switch, Route } from 'react-router-dom';
import { connect } from 'react-redux';
import { userPropType } from '../util/propTypes';
import { logErrorToRollbar } from './../util/util';

import {
    facilitiesRoute,
    mainRoute,
    USER_DEFAULT_STATE,
} from '../util/constants';

import FilterSidebar from './FilterSidebar';
import HomepageSidebar from './HomepageSidebar';

class SidebarWithErrorBoundary extends Component {
    state = { hasError: false };

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error) {
        const { user } = this.props;
        logErrorToRollbar(window, error, user);
    }

    render() {
        return (
            <Switch>
                <Route
                    key={JSON.stringify(this.state.hasError)}
                    exact
                    path={facilitiesRoute}
                    component={FilterSidebar}
                />
                <Route
                    key={JSON.stringify(this.state.hasError)}
                    exact
                    path={mainRoute}
                    component={HomepageSidebar}
                />
            </Switch>
        );
    }
}

SidebarWithErrorBoundary.propTypes = {
    user: userPropType,
};

SidebarWithErrorBoundary.defaultProps = {
    user: USER_DEFAULT_STATE,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
}) {
    return { user };
}

export default connect(mapStateToProps)(SidebarWithErrorBoundary);
