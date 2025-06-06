import React from 'react';
import { Link, Route, useLocation } from 'react-router-dom';
import { connect } from 'react-redux';
import { bool } from 'prop-types';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';

import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';
import ContributeForm from './ContributeForm';
import RequireAuthNotice from './RequireAuthNotice';

import { listsRoute, InfoLink, InfoPaths } from '../util/constants';
import { useResetScrollPosition } from '../util/hooks';

function ContributeList({ userHasSignedIn, fetchingSessionSignIn }) {
    const TITLE = 'Contribute';
    const location = useLocation();
    useResetScrollPosition(location);

    if (fetchingSessionSignIn) {
        return (
            <AppGrid title={TITLE}>
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <CircularProgress />
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    if (!userHasSignedIn) {
        return <RequireAuthNotice title={TITLE} />;
    }

    return (
        <AppOverflow>
            <AppGrid title="Upload">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <p>
                            Thank you for contributing your data to Open Supply
                            Hub.
                        </p>

                        <p>
                            <a
                                href={`${InfoLink}/${InfoPaths.preparingData}`}
                                target="_blank"
                                rel="noreferrer"
                            >
                                Please follow these step-by-step instructions
                            </a>{' '}
                            to prepare and upload your data to OS Hub via CSV or
                            Excel file.
                        </p>

                        <p>
                            Once you have read the instructions and prepared
                            your file, submit your list using the fields below.
                        </p>
                        <Paper
                            style={{
                                padding: '20px',
                                marginBottom: '20px',
                            }}
                        >
                            <Route component={ContributeForm} />
                        </Paper>
                        <Paper
                            style={{
                                padding: '20px',
                            }}
                        >
                            <div className="form__field">
                                <p className="form__label">
                                    Once the list has been successfully
                                    uploaded, you will receive an email letting
                                    you know{' '}
                                    <a
                                        href={`${InfoLink}/${InfoPaths.dataQuality}`}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        your list processing
                                    </a>{' '}
                                    is complete.
                                </p>
                            </div>
                            <div className="form__field">
                                <Link
                                    to={listsRoute}
                                    href={listsRoute}
                                    className="outlined-button outlined-button--link margin-top-16"
                                >
                                    View My Lists
                                </Link>
                            </div>
                        </Paper>
                    </Grid>
                </Grid>
            </AppGrid>
        </AppOverflow>
    );
}

ContributeList.propTypes = {
    userHasSignedIn: bool.isRequired,
    fetchingSessionSignIn: bool.isRequired,
};

function mapStateToProps({
    auth: {
        user: { user },
        session: { fetching },
    },
}) {
    return {
        userHasSignedIn: !user.isAnon,
        fetchingSessionSignIn: fetching,
    };
}

export default connect(mapStateToProps)(ContributeList);
