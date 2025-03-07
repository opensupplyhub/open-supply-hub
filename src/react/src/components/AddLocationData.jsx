import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';
import { withStyles, withTheme } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import AppGrid from './AppGrid';
import RequireAuthNotice from './RequireAuthNotice';

import { openInNewTab } from '../util/util';
import {
    InfoLink,
    InfoPaths,
    contributeProductionLocationRoute,
    multipleLocationRoute,
} from '../util/constants';
import { makeAddLocationStyles } from '../util/styles';

import MessyIcon from './MessyIcon';
import PlaylistIcon from './PlaylistIcon';
import PinDropIcon from './PinDropIcon';
import RectangleCardFigure from './RectangleCardFigure';
import SliceCardFigure from './SliceCardFigure';
import SliceMessyFigure from './SliceMessyFigure';
import SliceMessyDuoFigure from './SliceMessyDuoFigure';

function AddLocationData({ classes, userHasSignedIn, fetchingSessionSignIn }) {
    const TITLE = 'Contribute';
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
        <div className={classes.container}>
            <Typography variant="display3" className={classes.title}>
                Add production location data to OS Hub
            </Typography>
            <Typography variant="subheading" className={classes.description}>
                Contribute your data here to help build the world’s most
                complete, open and accessible map of global production:
            </Typography>
            <div className={classes.dataOptions}>
                <Paper className={classes.card}>
                    <div className={classes.cardRectangleView}>
                        <RectangleCardFigure />
                    </div>
                    <div>
                        <PlaylistIcon className={classes.cardIcon} />
                        <Typography
                            variant="headline"
                            className={classes.cardTitle}
                        >
                            Upload a dataset with multiple production locations
                            using{' '}
                            <span className={classes.highlight}>
                                a spreadsheet.
                            </span>
                        </Typography>
                        <Typography
                            variant="subheading"
                            className={classes.cardSub}
                        >
                            This option is best if you have a large number of
                            production locations to contribute.
                        </Typography>
                        <Button
                            color="secondary"
                            variant="text"
                            component={Link}
                            className={classes.buttonStyle}
                            to={multipleLocationRoute}
                        >
                            Upload Multiple Locations
                        </Button>
                        <div className={classes.messyData}>
                            <MessyIcon className={classes.messyIcon} />
                            <div className={classes.messyContent}>
                                <Typography
                                    variant="display1"
                                    className={classes.messyTitle}
                                >
                                    Have messy data?
                                </Typography>
                                <Typography
                                    variant="subheading"
                                    className={classes.messySub}
                                >
                                    We can get it ready for you. All you need to
                                    do is upload your data and we’ll take care
                                    of the rest.
                                </Typography>
                            </div>
                            <div className={classes.cardSliceDuoView}>
                                <SliceMessyDuoFigure />
                            </div>
                            <div className={classes.cardSliceView}>
                                <SliceMessyFigure />
                            </div>
                            <button
                                type="button"
                                className={classes.secondaryButton}
                                onClick={() =>
                                    openInNewTab(
                                        `${InfoLink}/${InfoPaths.contribute}`,
                                    )
                                }
                            >
                                Learn More
                            </button>
                        </div>
                    </div>
                </Paper>
                <Paper className={classes.card}>
                    <div>
                        <PinDropIcon className={classes.cardIcon} />
                        <Typography
                            variant="headline"
                            className={classes.cardTitle}
                        >
                            Add data for a
                            <br />
                            <span className={classes.highlight}>
                                single production location.
                            </span>
                        </Typography>
                        <Typography
                            variant="subheading"
                            className={classes.cardSub}
                        >
                            This option is best if you want to register your
                            production location or contribute data for one
                            production location at a time.
                        </Typography>
                        <Button
                            color="secondary"
                            variant="text"
                            component={Link}
                            className={classes.buttonStyle}
                            to={contributeProductionLocationRoute}
                        >
                            Add a Single Location
                        </Button>
                    </div>
                    <div className={classes.cardSliceView}>
                        <SliceCardFigure />
                    </div>
                </Paper>
            </div>
        </div>
    );
}

AddLocationData.propTypes = {
    classes: PropTypes.object.isRequired,
    userHasSignedIn: PropTypes.bool.isRequired,
    fetchingSessionSignIn: PropTypes.bool.isRequired,
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

export default connect(mapStateToProps)(
    withTheme()(withStyles(makeAddLocationStyles)(AddLocationData)),
);
