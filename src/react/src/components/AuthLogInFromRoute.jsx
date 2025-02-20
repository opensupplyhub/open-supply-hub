import React from 'react';
import { string } from 'prop-types';
import { Link } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import AppGrid from './AppGrid';

import { authLoginFormRoute, LOG_IN_TITLE } from '../util/constants';

export default function AuthLogInFromRoute({ title, text }) {
    return (
        <AppGrid title={title}>
            <Grid container className="margin-bottom-64">
                <Grid item xs={12}>
                    <Link to={authLoginFormRoute} href={authLoginFormRoute}>
                        {text}
                    </Link>
                </Grid>
            </Grid>
        </AppGrid>
    );
}

AuthLogInFromRoute.defaultProps = {
    title: '',
    text: LOG_IN_TITLE,
};

AuthLogInFromRoute.propTypes = {
    title: string,
    text: string,
};
