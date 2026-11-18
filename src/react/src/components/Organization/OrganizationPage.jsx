import React from 'react';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';

import AppGrid from '../AppGrid';
import AppOverflow from '../AppOverflow';
import RequireAuthNotice from '../RequireAuthNotice';
import OrganizationTab from './OrganizationTab';
import { USER_DEFAULT_STATE } from '../../util/constants';

const TITLE = 'My Organization';

/*
 * The My Organization page, opened from the account menu in the navbar.
 * It asks an anonymous visitor to log in, and shows everyone else their
 * invitations and, for a member, the organization itself.
 */
function OrganizationPage({ user, fetchingSessionSignIn }) {
    if (fetchingSessionSignIn) {
        return (
            <AppGrid title={TITLE}>
                <CircularProgress />
            </AppGrid>
        );
    }

    if (user.isAnon) {
        return (
            <RequireAuthNotice
                title={TITLE}
                text="Log in to see your organization"
            />
        );
    }

    return (
        <AppOverflow>
            <AppGrid title={TITLE}>
                <OrganizationTab />
            </AppGrid>
        </AppOverflow>
    );
}

OrganizationPage.defaultProps = {
    user: USER_DEFAULT_STATE,
};

function mapStateToProps({
    auth: {
        user: { user },
        session: { fetching },
    },
}) {
    return {
        user,
        fetchingSessionSignIn: fetching,
    };
}

export default connect(mapStateToProps)(OrganizationPage);
