import React from 'react';
import { connect } from 'react-redux';
import { withStyles, withTheme } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import MessyIcon from './MessyIcon';
import COLOURS from '../util/COLOURS';

const addLocationStyles = theme =>
    Object.freeze({
        buttonStyles: Object.freeze({
            margin: '5px',
            display: 'center',
            fontWeight: 'bold',
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

function AddLocationData({ classes }) {
    const styles = {
        title: {
            paddingLeft: '5%',
            paddingRight: '5%',
            color: COLOURS.NEAR_BLACK,
            fontWeight: 'bold',
            marginBottom: '1rem',
        },
        description: {
            paddingLeft: '5%',
            paddingRight: '5%',
            marginBottom: '2rem',
            fontWeight: 'bold',
        },
        dataOptions: {
            display: 'flex',
            justifyContent: 'center',
            gap: '25px',
            paddingBottom: '5%',
            flexWrap: 'wrap',
        },
        card: {
            backgroundColor: COLOURS.WHITE,
            padding: '0',
            width: '35%',
            textAlign: 'center',
        },
        cardTitle: {
            fontSize: '32px',
            margin: '5%',
        },
        cardSub: {
            fontSize: '16px',
            margin: '5%',
        },
        highlight: {
            color: COLOURS.NEAR_BLACK,
            fontWeight: 'bold',
        },
        messyData: {
            backgroundColor: '#8428FA21',
            margin: '20px',
            marginTop: '50px',
            display: 'flex', // Use flexbox for icon, text, and button alignment
            alignItems: 'center', // Vertically align items
            padding: '20px',
            position: 'relative', // Allow button positioning
        },
        messyContent: {
            display: 'flex', // Align icon and text horizontally
            flexDirection: 'column', // Stack text vertically
            marginLeft: '15px', // Add space between icon and text
            textAlign: 'left',
            flex: 1, // Take up available space
        },
        messyIcon: {
            color: COLOURS.NEAR_BLACK,
        },
        messyTitle: {
            color: COLOURS.NEAR_BLACK,
            marginBottom: '10px',
            maxWidth: '75%',
        },
        messySub: {
            color: COLOURS.NEAR_BLACK,
            marginBottom: '20px',
            maxWidth: '75%',
        },
        secondaryButton: {
            backgroundColor: COLOURS.WHITE,
            color: COLOURS.NEAR_BLACK,
            fontWeight: 'bold',
            border: 'none',
            padding: '0.5rem 1rem',
            cursor: 'pointer',
            borderRadius: '4px',
            position: 'absolute',
            right: '20px', // Align to the right
            top: '50%', // Vertically center relative to the container
            transform: 'translateY(-50%)',
        },
    };

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
                    <div>
                        <Typography variant="heading" style={styles.cardTitle}>
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
                            variant="contained"
                            className={classes.buttonStyles}
                            // disabled={!stepInputIsValid(formData)}
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
                                    variant="display"
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
                            >
                                Learn More
                            </button>
                        </div>
                    </div>
                </Paper>
                {/* Single Location */}
                <Paper style={styles.card}>
                    <div>
                        <h2 style={styles.cardTitle}>
                            Add data for a{' '}
                            <strong>single production location</strong>.
                        </h2>
                        <p>
                            This option is best if you want to register your
                            production location or contribute data for one
                            production location at a time.
                        </p>
                        <Button
                            color="secondary"
                            variant="contained"
                            className={classes.buttonStyles}
                            // disabled={!stepInputIsValid(formData)}
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
