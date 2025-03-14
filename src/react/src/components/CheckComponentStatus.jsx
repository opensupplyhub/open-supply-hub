import React from 'react';
import { arrayOf, string } from 'prop-types';
import CircularProgress from '@material-ui/core/CircularProgress';
import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';
import RequireAuthNotice from './RequireAuthNotice';

export const LoadingIndicator = ({ title }) => (
    <AppOverflow>
        <AppGrid title={title}>
            <CircularProgress />
        </AppGrid>
    </AppOverflow>
);

LoadingIndicator.propTypes = {
    title: string.isRequired,
};

export const AuthNotice = ({ title, text }) => (
    <AppOverflow>
        <RequireAuthNotice title={title} text={text} />
    </AppOverflow>
);

AuthNotice.defaultProps = {
    text: 'Sign in to view your Open Supply Hub facility claims.',
};

AuthNotice.propTypes = {
    title: string.isRequired,
    text: string,
};

export const ErrorsList = ({ title, errors }) => (
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
