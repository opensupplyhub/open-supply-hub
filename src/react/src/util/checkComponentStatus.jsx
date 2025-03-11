import React from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import AppGrid from '../components/AppGrid';
import AppOverflow from '../components/AppOverflow';
import RequireAuthNotice from '../components/RequireAuthNotice';

const LoadingIndicator = ({ title }) => (
    <AppOverflow>
        <AppGrid title={title}>
            <CircularProgress />
        </AppGrid>
    </AppOverflow>
);

const AuthNotice = ({ title }) => (
    <AppOverflow>
        <RequireAuthNotice
            title={title}
            text="Sign in to view your Open Supply Hub facility claims."
        />
    </AppOverflow>
);

const ErrorsList = ({ title, errors }) => (
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

export default {
    LoadingIndicator,
    AuthNotice,
    ErrorsList,
};
