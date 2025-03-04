import React from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import AppGrid from '../components/AppGrid';
import AppOverflow from '../components/AppOverflow';
import RequireAuthNotice from '../components/RequireAuthNotice';

const renderIfFetchStatus = (fetchingStatus, title) => {
    if (fetchingStatus) {
        return (
            <AppOverflow>
                <AppGrid title={title}>
                    <CircularProgress />
                </AppGrid>
            </AppOverflow>
        );
    }

    return null;
};

const renderIfNotAuthStatus = (userHasSignedIn, title) => {
    if (!userHasSignedIn) {
        return (
            <AppOverflow>
                <RequireAuthNotice
                    title={title}
                    text="Sign in to view your Open Supply Hub lists"
                />
            </AppOverflow>
        );
    }
    return null;
};
const renderIfErrorsStatus = (errors, title) => {
    if (errors) {
        return (
            <AppOverflow>
                <AppGrid title={title}>
                    <ul>
                        {errors.map(err => (
                            <li key={err}>{err}</li>
                        ))}
                    </ul>
                </AppGrid>
            </AppOverflow>
        );
    }
    return null;
};

export default {
    renderIfFetchStatus,
    renderIfNotAuthStatus,
    renderIfErrorsStatus,
};
