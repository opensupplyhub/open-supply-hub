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
import {
    claimDetailsRoute,
    facilityDetailsRoute,
} from '../../../util/constants';
import { resetClaimForm } from '../../../actions/claimForm';
import { resetFilterOptions } from '../../../actions/filterOptions';
import { resetSingleProductionLocation } from '../../../actions/contributeProductionLocation';

const ClaimIntro = ({
    classes,
    history,
    osID,
    userHasSignedIn,
    resetForm,
    resetFilters,
    resetProductionLocation,
}) => {
    if (!userHasSignedIn) {
        return (
            <RequireAuthNotice
                title="Claim this production location"
                text="Log in to claim a production location on Open Supply Hub"
            />
        );
    }

    const handleGoBack = () => {
        // Reset form, filters, and production location data when going back.
        resetForm();
        resetFilters();
        resetProductionLocation();

        history.push(facilityDetailsRoute.replace(':osID', osID));
    };

    const handleContinue = () => {
        // Set session storage flag to allow access to claim form.
        sessionStorage.setItem(`claim-form-access-${osID}`, 'true');
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
    resetForm: PropTypes.func.isRequired,
    resetFilters: PropTypes.func.isRequired,
    resetProductionLocation: PropTypes.func.isRequired,
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

const mapDispatchToProps = dispatch => ({
    resetForm: () => dispatch(resetClaimForm()),
    resetFilters: () => dispatch(resetFilterOptions()),
    resetProductionLocation: () => dispatch(resetSingleProductionLocation()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withRouter(withStyles(claimIntroStyles)(withScrollReset(ClaimIntro))));
