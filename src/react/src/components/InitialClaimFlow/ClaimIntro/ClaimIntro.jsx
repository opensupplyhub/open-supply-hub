import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { withRouter } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import ClaimInfoSection from './ClaimInfoSection';
import AppOverflow from '../../AppOverflow';
import RequireAuthNotice from '../../RequireAuthNotice';
import { claimIntroStyles } from './styles';
import withScrollReset from '../HOCs/withScrollReset';
import { resetClaimForm, updateOsIdToClaim } from '../../../actions/claimForm';
import {
    claimDetailsRoute,
    facilityDetailsRoute,
} from '../../../util/constants';
import useClaimIntroOsIdTracking from './hooks';

const ClaimIntro = ({
    classes,
    history,
    osID,
    userHasSignedIn,
    resetForm,
    updateOsId,
    osIdToClaim,
}) => {
    // Track OS ID changes and reset form when switching between locations.
    useClaimIntroOsIdTracking(osID, osIdToClaim, updateOsId, resetForm);

    if (!userHasSignedIn) {
        return (
            <RequireAuthNotice
                title="Claim this production location"
                text="Log in to claim a production location on Open Supply Hub"
            />
        );
    }

    const handleGoBack = () => {
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
                            In order to submit a claim request, you must be an
                            owner, manager, have supervisor approval or be an
                            authorized representative of the parent company of
                            the production location.
                        </Typography>
                    </div>
                    <ClaimInfoSection>
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
                                Continue
                            </Button>
                        </div>
                    </ClaimInfoSection>
                </div>
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
    updateOsId: PropTypes.func.isRequired,
    osIdToClaim: PropTypes.string.isRequired,
};

const mapStateToProps = (
    {
        auth: {
            user: { user },
        },
        claimForm: { osIdToClaim },
    },
    {
        match: {
            params: { osID },
        },
    },
) => ({
    osID,
    userHasSignedIn: !user.isAnon,
    osIdToClaim,
});

export const mapDispatchToProps = dispatch => ({
    resetForm: () => dispatch(resetClaimForm()),
    updateOsId: osID => dispatch(updateOsIdToClaim(osID)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withRouter(withStyles(claimIntroStyles)(withScrollReset(ClaimIntro))));
