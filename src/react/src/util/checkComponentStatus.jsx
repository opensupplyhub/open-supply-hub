import React from 'react';
import { arrayOf, string } from 'prop-types';
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

LoadingIndicator.propTypes = {
    title: string.isRequired,
};

const AuthNotice = ({ title }) => (
    <AppOverflow>
        <RequireAuthNotice
            title={title}
            text="Sign in to view your Open Supply Hub facility claims."
        />
    </AppOverflow>
);

AuthNotice.propTypes = {
    title: string.isRequired,
};

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

ErrorsList.defaultProps = {
    errors: null,
};

ErrorsList.propTypes = {
    title: string.isRequired,
    errors: arrayOf(string),
};

export default {
    LoadingIndicator,
    AuthNotice,
    ErrorsList,
};
