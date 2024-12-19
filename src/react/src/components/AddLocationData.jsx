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
// import RectangleCardFigure from './RectangleCardFigure';
import COLOURS from '../util/COLOURS';

const addLocationStyles = theme =>
    Object.freeze({
        buttonStyles: Object.freeze({
            textTransform: 'none',
            borderRadius: 0,
            margin: '15px',
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
            paddingTop: '15px',
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
            padding: '60px 25px 25px 25px', // Add padding for spacing
            width: '45%',
            textAlign: 'center',
            display: 'flex', // Use flexbox
            flexDirection: 'column', // Stack children vertically
            alignItems: 'center', // Center horizontally
            justifyContent: 'center', // Center vertically
        },
        cardTitle: {
            fontSize: '32px',
            margin: '0 auto', // Center horizontally with auto margins
            maxWidth: '80%', // Adjust the max width if needed
            textAlign: 'center', // Ensure text alignment is centered
            paddingTop: '15px',
            paddingBottom: '15px',
            fontWeight: '300',
            lineHeight: '1.0',
        },
        cardSub: {
            fontSize: '16px',
            margin: '0 auto', // Center horizontally with auto margins
            maxWidth: '50%', // Adjust the max width if needed
            textAlign: 'center', // Ensure text alignment is centered
            paddingBottom: '5px',
            fontWeight: '600',
        },
        cardRectangle: {
            position: 'absolute',
            top: '-30px', // Position above the card
            left: '50%', // Center horizontally
            transform: 'translateX(-50%)', // Adjust for centering
            width: '60px', // Adjust size as needed
            height: '60px', // Adjust size as needed
            backgroundColor: '#FFB6C1', // Example color for the rectangle
            zIndex: 1, // Ensure it is above the card
        },
        cardIcon: {
            color: COLOURS.NEAR_BLACK,
        },
        highlight: {
            color: COLOURS.NEAR_BLACK,
            fontWeight: '600',
        },
        messyData: {
            backgroundColor: '#8428FA21',
            marginTop: '50px',
            display: 'flex', // Use flexbox for icon, text, and button alignment
            alignItems: 'center', // Vertically align items
            padding: '30px',
            position: 'relative', // Allow button positioning
            maxHeight: '56px',
        },
        messyContent: {
            display: 'flex', // Align icon and text horizontally
            flexDirection: 'column', // Stack text vertically
            marginLeft: '20px', // Add space between icon and text
            textAlign: 'left',
            flex: 1, // Take up available space
        },
        messyTitle: {
            color: COLOURS.NEAR_BLACK,
            maxWidth: '75%',
        },
        messySub: {
            color: COLOURS.NEAR_BLACK,
            marginBottom: '10px',
            maxWidth: '75%',
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
            right: '20px', // Align to the right
            top: '50%', // Vertically center relative to the container
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
                    {/* <RectangleCardFigure style={styles.cardRectangle} /> */}
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
