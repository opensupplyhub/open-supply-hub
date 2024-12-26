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

import { openInNewTab } from '../util/util';
import {
    authLoginFormRoute,
    InfoLink,
    InfoPaths,
    contributeProductionLocationRoute,
    multipleLocationRoute,
} from '../util/constants';

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
        buttonStyle: Object.freeze({
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
        title: Object.freeze({
            paddingLeft: '5%',
            paddingRight: '5%',
            paddingTop: '25px',
            color: COLOURS.NEAR_BLACK,
            fontWeight: 'bold',
            marginBottom: '1rem',
        }),
        description: Object.freeze({
            paddingLeft: '5%',
            paddingRight: '5%',
            paddingTop: '5px',
            marginBottom: '2rem',
            fontWeight: 'bold',
        }),
        dataOptions: Object.freeze({
            display: 'flex',
            paddingLeft: '5%',
            paddingRight: '5%',
            gap: '50px',
            paddingBottom: '5%',
            flexWrap: 'wrap',
            flexDirection: 'row',
            [theme.breakpoints.down('md')]: {
                flexDirection: 'column',
                display: 'center',
            },
        }),
        card: Object.freeze({
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
        }),
        cardTitle: Object.freeze({
            fontSize: '32px',
            margin: '0 auto',
            maxWidth: '80%',
            textAlign: 'center',
            paddingTop: '15px',
            paddingBottom: '15px',
            fontWeight: '300',
            lineHeight: '1.0',
        }),
        cardSub: Object.freeze({
            fontSize: '16px',
            margin: '0 auto',
            maxWidth: '50%',
            textAlign: 'center',
            paddingBottom: '5px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        cardRectangleView: Object.freeze({
            position: 'absolute',
            top: 0,
            right: 0,
        }),
        cardSliceView: Object.freeze({
            position: 'absolute',
            bottom: -5,
            right: 0,
        }),
        cardSliceDuoView: Object.freeze({
            position: 'absolute',
            top: 0,
            right: '25%',
        }),
        cardIcon: Object.freeze({
            color: COLOURS.NEAR_BLACK,
            textAlign: 'center',
            alignItems: 'center',
        }),
        highlight: Object.freeze({
            color: COLOURS.NEAR_BLACK,
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        messyData: Object.freeze({
            backgroundColor: COLOURS.LIGHT_PURPLE,
            marginTop: '50px',
            display: 'flex',
            alignItems: 'center',
            flexDirection: 'row',
            padding: '30px',
            position: 'relative',
            maxHeight: '56px',
            [theme.breakpoints.down('md')]: {
                flexDirection: 'column',
                maxHeight: '25%',
            },
        }),
        messyContent: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            marginLeft: '20px',
            textAlign: 'left',
            flex: 1,
        }),
        messyTitle: Object.freeze({
            color: COLOURS.NEAR_BLACK,
            maxWidth: '75%',
            fontWeight: theme.typography.fontWeightSemiBold,
            fontSize: '24px',
            [theme.breakpoints.down('md')]: {
                fontSize: '16px',
                textAlign: 'center',
                maxWidth: '100%',
            },
        }),
        messySub: Object.freeze({
            color: COLOURS.NEAR_BLACK,
            marginBottom: '10px',
            maxWidth: '65%',
            fontWeight: theme.typography.fontWeightSemiBold,
            fontSize: '16px',
            [theme.breakpoints.down('md')]: {
                fontSize: '12px',
                textAlign: 'center',
                maxWidth: '100%',
            },
        }),
        messyIcon: Object.freeze({
            color: COLOURS.NEAR_BLACK,
        }),
        secondaryButton: Object.freeze({
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
            [theme.breakpoints.down('md')]: {
                fontSize: '12px',
                position: 'relative',
                right: '0px',
                top: '20px',
            },
        }),
    });

function AddLocationData({ classes, userHasSignedIn, fetchingSessionSignIn }) {
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
                            variant="heading"
                            className={classes.cardTitle}
                        >
                            Upload a dataset with multiple production locations
                            using a{' '}
                            <span className={classes.highlight}>
                                spreadsheet.
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
                            variant="heading"
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
                            disabled
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
    withTheme()(withStyles(addLocationStyles)(AddLocationData)),
);
