import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { withStyles, withTheme } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import AppGrid from './AppGrid';

import { openInNewTab } from '../util/util';
import { authLoginFormRoute, InfoLink, InfoPaths } from '../util/constants';

import MessyIcon from './MessyIcon';
import PlaylistIcon from './PlaylistIcon';
import PinDropIcon from './PinDropIcon';
import RectangleCardFigure from './RectangleCardFigure';
import SliceCardFigure from './SliceCardFigure';
import SliceMessyFigure from './SliceMessyFigure';
import SliceMessyDuoFigure from './SliceMessyDuoFigure';
import COLOURS from '../util/COLOURS';

const addLocationStyles = theme =>
    Object.freeze({
        buttonStyles: Object.freeze({
            textTransform: 'none',
            borderRadius: 0,
            margin: '20px',
            padding: '15px 25px 15px 25px',
            display: 'center',
            fontWeight: '900',
            fontSize: '16px',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
        container: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREY,
        }),
    });

function AddLocationData({ classes, userHasSignedIn, fetchingSessionSignIn }) {
    const styles = {
        title: {
            paddingLeft: '5%',
            paddingRight: '5%',
            paddingTop: '25px',
            color: COLOURS.NEAR_BLACK,
            fontWeight: 'bold',
            marginBottom: '1rem',
        },
        description: {
            paddingLeft: '5%',
            paddingRight: '5%',
            paddingTop: '5px',
            marginBottom: '2rem',
            fontWeight: 'bold',
        },
        dataOptions: {
            display: 'flex',
            paddingLeft: '5%',
            paddingRight: '5%',
            gap: '50px',
            paddingBottom: '5%',
            flexWrap: 'wrap',
        },
        card: {
            backgroundColor: COLOURS.WHITE,
            boxShadow: 'none',
            padding: '60px 25px 25px 25px',
            width: '45%',
            position: 'relative',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
        },
        cardTitle: {
            fontSize: '32px',
            margin: '0 auto',
            maxWidth: '80%',
            textAlign: 'center',
            paddingTop: '15px',
            paddingBottom: '15px',
            fontWeight: '300',
            lineHeight: '1.0',
        },
        cardSub: {
            fontSize: '16px',
            margin: '0 auto',
            maxWidth: '50%',
            textAlign: 'center',
            paddingBottom: '5px',
            fontWeight: '600',
        },
        cardRectangleView: {
            position: 'absolute',
            top: 0,
            right: 0,
        },
        cardSliceView: {
            position: 'absolute',
            bottom: -5,
            right: 0,
        },
        cardSliceDuoView: {
            position: 'absolute',
            top: 0,
            right: '25%',
        },
        cardIcon: {
            color: COLOURS.NEAR_BLACK,
            textAlign: 'center',
            alignItems: 'center',
        },
        highlight: {
            color: COLOURS.NEAR_BLACK,
            fontWeight: '600',
        },
        messyData: {
            backgroundColor: '#8428FA21',
            marginTop: '50px',
            display: 'flex',
            alignItems: 'center',
            padding: '30px',
            position: 'relative',
            maxHeight: '56px',
        },
        messyContent: {
            display: 'flex',
            flexDirection: 'column',
            marginLeft: '20px',
            textAlign: 'left',
            flex: 1,
        },
        messyTitle: {
            color: COLOURS.NEAR_BLACK,
            maxWidth: '75%',
            fontWeight: '600',
        },
        messySub: {
            color: COLOURS.NEAR_BLACK,
            marginBottom: '10px',
            maxWidth: '65%',
            fontWeight: '600',
        },
        messyIcon: {
            color: COLOURS.NEAR_BLACK,
        },
        secondaryButton: {
            backgroundColor: COLOURS.WHITE,
            color: COLOURS.NEAR_BLACK,
            fontWeight: '900',
            fontSize: '16px',
            border: 'none',
            padding: '1rem 1.5rem',
            cursor: 'pointer',
            position: 'absolute',
            right: '20px',
            top: '50%',
            transform: 'translateY(-50%)',
        },
    };

    if (fetchingSessionSignIn) {
        return (
            <AppGrid title="Contribute">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <CircularProgress />
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    if (!userHasSignedIn) {
        return (
            <AppGrid title="Contribute">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <Link to={authLoginFormRoute} href={authLoginFormRoute}>
                            Log in to contribute to Open Supply Hub
                        </Link>
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    return (
        <div className={classes.container}>
            <Typography variant="display3" style={styles.title}>
                Add production location data to OS Hub
            </Typography>
            <Typography variant="subheading" style={styles.description}>
                Contribute your data here to help build the world’s most
                complete, open and accessible map of global production:
            </Typography>
            <div style={styles.dataOptions}>
                {/* Multiple Locations */}
                <Paper style={styles.card}>
                    <div style={styles.cardRectangleView}>
                        <RectangleCardFigure />
                    </div>
                    <div>
                        <PlaylistIcon style={styles.cardIcon} />
                        <Typography variant="display" style={styles.cardTitle}>
                            Upload a dataset with multiple production locations
                            using a{' '}
                            <span style={styles.highlight}>spreadsheet</span>.
                        </Typography>
                        <Typography variant="subheading" style={styles.cardSub}>
                            This option is best if you have a large number of
                            production locations to contribute.
                        </Typography>
                        <Button
                            color="secondary"
                            variant="text"
                            component={Link}
                            className={classes.buttonStyles}
                            to="/contribute/multiple-locations"
                        >
                            Upload Multiple Locations
                        </Button>
                        {/* Messy Data Section */}
                        <div style={styles.messyData}>
                            {/* Icon on the left */}
                            <MessyIcon style={styles.messyIcon} />
                            {/* Text content */}
                            <div style={styles.messyContent}>
                                <Typography
                                    variant="display1"
                                    style={styles.messyTitle}
                                >
                                    Have messy data?
                                </Typography>
                                <Typography
                                    variant="subheading"
                                    style={styles.messySub}
                                >
                                    We can get it ready for you. All you need to
                                    do is upload your data and we’ll take care
                                    of the rest.
                                </Typography>
                            </div>
                            <div style={styles.cardSliceDuoView}>
                                <SliceMessyDuoFigure />
                            </div>
                            <div style={styles.cardSliceView}>
                                <SliceMessyFigure />
                            </div>
                            {/* Button on the right */}
                            <button
                                type="button"
                                style={styles.secondaryButton}
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
                {/* Single Location */}
                <Paper style={styles.card}>
                    <div>
                        <PinDropIcon style={styles.cardIcon} />
                        <Typography variant="display" style={styles.cardTitle}>
                            Add data for a
                            <br />
                            <span style={styles.highlight}>
                                single production location.
                            </span>
                        </Typography>
                        <Typography variant="subheading" style={styles.cardSub}>
                            This option is best if you want to register your
                            production location or contribute data for one
                            production location at a time.
                        </Typography>
                        <Button
                            color="secondary"
                            variant="text"
                            className={classes.buttonStyles}
                            disabled="true"
                        >
                            Add a Single Location
                        </Button>
                    </div>
                    <div style={styles.cardSliceView}>
                        <SliceCardFigure />
                    </div>
                </Paper>
            </div>
        </div>
    );
}

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
    withTheme()(withStyles(addLocationStyles)(AddLocationData)),
);
