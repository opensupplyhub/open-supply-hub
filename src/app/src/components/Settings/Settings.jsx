import React, { useState } from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import UserNotifications from '../UserNotifications';
import UserProfile from '../UserProfile';
import UserAPITokens from '../UserAPITokens';
import UserAPIInfo from '../UserApiInfo';
import AppOverflow from '../AppOverflow';
import AppGrid from '../AppGrid';
import SettingTabs from './SettingTabs';
import EmbeddedMapConfigWrapper from '../EmbeddedMapConfigWrapper';

import { userPropType } from '../../util/propTypes';
import { authLoginFormRoute, USER_DEFAULT_STATE } from '../../util/constants';
import { convertFeatureFlagsObjectToListOfActiveFlags } from '../../util/util';
import { getTabs } from './utils';
import {
    PROFILE_TAB,
    EMBED_TAB,
    API_TAB,
    NOTIFICATIONS_TAB,
} from './constants';

function Settings({
    user,
    fetchingSessionSignIn,
    activeFeatureFlags,
    fetchingFlags,
}) {
    const [activeTabIndex, setActiveTabIndex] = useState(0);
    const handleTabChange = (e, tab) => setActiveTabIndex(tab);

    const tabs = getTabs({ fetchingFlags, activeFeatureFlags, user });

    if (fetchingSessionSignIn) {
        return (
            <AppGrid title="Settings">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <CircularProgress />
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    if (!user) {
        return (
            <AppGrid title="Settings">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <Link to={authLoginFormRoute} href={authLoginFormRoute}>
                            Log in to update your settings
                        </Link>
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    return (
        <>
            <AppGrid title="Settings">
                <SettingTabs
                    value={activeTabIndex}
                    onChange={handleTabChange}
                    tabs={tabs}
                />
            </AppGrid>
            <AppOverflow>
                {!user.isAnon && tabs[activeTabIndex] === PROFILE_TAB && (
                    <UserProfile allowEdits id={user.id.toString()} />
                )}
                {tabs[activeTabIndex] === EMBED_TAB && (
                    <EmbeddedMapConfigWrapper />
                )}
                {tabs[activeTabIndex] === API_TAB && (
                    <AppGrid>
                        <UserAPITokens />
                        <UserAPIInfo uid={user.id} />
                    </AppGrid>
                )}
                {!user.isAnon && tabs[activeTabIndex] === NOTIFICATIONS_TAB && (
                    <UserNotifications />
                )}
            </AppOverflow>
        </>
    );
}

Settings.defaultProps = {
    user: USER_DEFAULT_STATE,
};

Settings.propTypes = {
    user: userPropType,
};

function mapStateToProps({
    auth: {
        user: { user },
        session: { fetching },
    },
    featureFlags: { fetching: fetchingFlags, flags },
}) {
    return {
        user,
        fetchingSessionSignIn: fetching,
        activeFeatureFlags: convertFeatureFlagsObjectToListOfActiveFlags(flags),
        fetchingFlags,
    };
}

export default connect(mapStateToProps)(Settings);
