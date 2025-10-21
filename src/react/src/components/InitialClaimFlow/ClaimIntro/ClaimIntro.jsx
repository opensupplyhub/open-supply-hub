import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { withRouter } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import ArrowForwardIcon from '@material-ui/icons/ArrowForward';

import ClaimInfoSection from './ClaimInfoSection';
import AppGrid from '../../AppGrid';
import AppOverflow from '../../AppOverflow';
import RequireAuthNotice from '../../RequireAuthNotice';
import { claimIntroStyles } from './styles';
import withScrollReset from '../HOCs/withScrollReset';
import { claimDetailsRoute } from '../../../util/constants';

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
        history.push(claimDetailsRoute.replace(':osID', osID));
    };

    return (
        <div className={classes.root}>
            <AppOverflow>
                <AppGrid>
                    <div className={classes.container}>
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
                        <ClaimInfoSection />
                        <div className={classes.actionsContainer}>
                            <div className={classes.actionsInner}>
                                <Button
                                    variant="outlined"
                                    className={classes.backButton}
                                    onClick={handleGoBack}
                                >
                                    Go Back
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
    osID: PropTypes.string.isRequired,
    userHasSignedIn: PropTypes.bool.isRequired,
    classes: PropTypes.object.isRequired,
    history: PropTypes.shape({
        goBack: PropTypes.func.isRequired,
        push: PropTypes.func.isRequired,
    }).isRequired,
};

const mapStateToProps = (
    {
        auth: {
            user: { user },
        },
    },
    {
        match: {
            params: { osID },
        },
    },
) => ({
    osID,
    userHasSignedIn: !user.isAnon,
});

export default connect(mapStateToProps)(
    withRouter(withStyles(claimIntroStyles)(withScrollReset(ClaimIntro))),
);
