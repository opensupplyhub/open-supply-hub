import React from 'react';
import { string } from 'prop-types';
import { Link, useLocation } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import AppGrid from './AppGrid';

import { authLoginFormRoute } from '../util/constants';

export default function RequireAuthNotice({ title, text }) {
    const { pathname } = useLocation();

    return (
        <AppGrid title={title}>
            <Grid container className="margin-bottom-64">
                <Grid item xs={12}>
                    <Link
                        to={{
                            pathname: authLoginFormRoute,
                            state: { prevPath: pathname },
                        }}
                        href={authLoginFormRoute}
                    >
                        {text}
                    </Link>
                </Grid>
            </Grid>
        </AppGrid>
    );
}

RequireAuthNotice.defaultProps = {
    title: 'Unauthorized Access',
    text: 'Log in to contribute to Open Supply Hub',
};

RequireAuthNotice.propTypes = {
    title: string,
    text: string,
};
