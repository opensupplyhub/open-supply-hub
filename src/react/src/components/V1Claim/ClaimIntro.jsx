import React from 'react';
import { connect } from 'react-redux';
import { string, bool } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { withRouter } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import ArrowForwardIcon from '@material-ui/icons/ArrowForward';

import ClaimInfoSection from './ClaimInfoSection';
import AppGrid from '../AppGrid';
import AppOverflow from '../AppOverflow';
import { makeClaimDetailsLink } from '../../util/util';
import RequireAuthNotice from '../RequireAuthNotice';
import COLOURS from '../../util/COLOURS';

const claimIntroStyles = theme => ({
    root: {
        backgroundColor: COLOURS.LIGHT_GREY,
        minHeight: 'calc(100vh - 64px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: theme.spacing.unit * 0,
        paddingBottom: theme.spacing.unit * 4,
    },
    container: {
        maxWidth: 1440,
        width: '100%',
        padding: theme.spacing.unit * 2,
        [theme.breakpoints.down('sm')]: {
            padding: theme.spacing.unit * 2,
        },
    },
    heroSection: {
        textAlign: 'center',
        marginBottom: theme.spacing.unit * 3,
        marginTop: 0,
        paddingTop: 0,
    },
    title: {
        fontSize: 30,
        fontWeight: 700,
        color: '#191919',
        marginBottom: theme.spacing.unit,
        [theme.breakpoints.down('sm')]: {
            fontSize: 24,
        },
    },
    subtitle: {
        fontSize: 18,
        color: '#666',
        maxWidth: 720,
        margin: '0 auto',
        lineHeight: 1.6,
    },
    actionsContainer: {
        backgroundColor: '#fff',
        borderRadius: theme.spacing.unit,
        padding: theme.spacing.unit * 2,
        marginTop: theme.spacing.unit * 3,
        marginBottom: 0,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e0e0e0',
    },
    actionsInner: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        [theme.breakpoints.down('sm')]: {
            flexDirection: 'column',
            gap: theme.spacing.unit * 2,
        },
    },
    backButton: {
        padding: '10px 24px',
        fontSize: 16,
        fontWeight: 800,
        borderColor: '#ccc',
        textTransform: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: '8px !important',
        '&:hover': {
            backgroundColor: '#f5f5f5',
            borderColor: '#999',
        },
        [theme.breakpoints.down('sm')]: {
            width: '100%',
        },
    },
    continueButton: {
        padding: '10px 24px',
        fontSize: 18,
        fontWeight: 800,
        backgroundColor: '#FFD700',
        color: '#000',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        textTransform: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: '8px !important',
        '&:hover': {
            backgroundColor: '#FFC700',
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
        },
        [theme.breakpoints.down('sm')]: {
            width: '100%',
        },
    },
    icon: {
        marginLeft: theme.spacing.unit,
        fontSize: 20,
        fontWeight: 800,
        display: 'flex',
        alignItems: 'center',
    },
});

const ClaimIntro = ({ classes, history, osID, userHasSignedIn }) => {
    if (!userHasSignedIn) {
        return (
            <RequireAuthNotice
                title="Claim this production location"
                text="Log in to claim a production location on Open Supply Hub"
            />
        );
    }

    const handleGoBack = () => {
        history.goBack();
    };

    const handleContinue = () => {
        history.push(makeClaimDetailsLink(osID));
    };

    return (
        <div className={classes.root}>
            <AppOverflow>
                <AppGrid>
                    <div className={classes.container}>
                        {/* Hero Section */}
                        <div className={classes.heroSection}>
                            <Typography
                                variant="title"
                                className={classes.title}
                                component="h1"
                            >
                                Claim a Production Location
                            </Typography>
                            <Typography
                                variant="subheading"
                                className={classes.subtitle}
                            >
                                In order to submit a claim request, you must be
                                an owner, manager, have supervisor approval or
                                be an authorized representative of the parent
                                company of the production location.
                            </Typography>
                        </div>

                        {/* Claim Info Steps */}
                        <ClaimInfoSection />

                        {/* Action Buttons */}
                        <div className={classes.actionsContainer}>
                            <div className={classes.actionsInner}>
                                <Button
                                    variant="outlined"
                                    className={classes.backButton}
                                    onClick={handleGoBack}
                                >
                                    GO BACK
                                </Button>
                                <Button
                                    variant="contained"
                                    className={classes.continueButton}
                                    onClick={handleContinue}
                                >
                                    Continue to Claim Form
                                    <ArrowForwardIcon
                                        className={classes.icon}
                                    />
                                </Button>
                            </div>
                        </div>
                    </div>
                </AppGrid>
            </AppOverflow>
        </div>
    );
};

ClaimIntro.propTypes = {
    osID: string.isRequired,
    userHasSignedIn: bool.isRequired,
};

const mapStateToProps = (
    state,
    {
        match: {
            params: { osID },
        },
    },
) => ({
    osID,
    userHasSignedIn: !state.auth.user.user.isAnon,
});

export default connect(mapStateToProps)(
    withRouter(withStyles(claimIntroStyles)(ClaimIntro)),
);
