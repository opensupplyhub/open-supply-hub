import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { withRouter } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import ClaimInfoSection from './ClaimInfoSection';
import AppOverflow from '../../AppOverflow';
import ModerationPauseBanner from '../../ModerationPauseBanner';
import RequireAuthNotice from '../../RequireAuthNotice';
import ClaimCampaignBanner from '../ClaimCampaignBanner/ClaimCampaignBanner';
import { claimIntroStyles } from './styles';
import withScrollReset from '../HOCs/withScrollReset';
import {
    resetClaimForm,
    updateOsIdToClaim,
    updateClaimFormField,
} from '../../../actions/claimForm';
import {
    claimDetailsRoute,
    facilityDetailsRoute,
    CLAIM_CAMPAIGNS,
} from '../../../util/constants';
import { convertFeatureFlagsObjectToListOfActiveFlags } from '../../../util/util';
import useClaimIntroOsIdTracking from './hooks';

const ClaimIntro = ({
    classes,
    history,
    location,
    osID,
    userHasSignedIn,
    resetForm,
    updateOsId,
    osIdToClaim,
    campaignCode,
    campaignFlagActive,
    setCampaignCode,
}) => {
    // Track OS ID changes and reset form when switching between locations.
    useClaimIntroOsIdTracking(osID, osIdToClaim, updateOsId, resetForm);

    // Attach an optional claim campaign code from the URL to the form.
    useEffect(() => {
        const campaign = new URLSearchParams(location.search).get('campaign');
        if (campaign && campaignFlagActive) {
            setCampaignCode(campaign);
        }
    }, [location.search, campaignFlagActive, setCampaignCode]);

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
        <div className={`${classes.root} notranslate`} translate="no">
            <ModerationPauseBanner />
            <AppOverflow>
                <div className={classes.container}>
                    <ClaimCampaignBanner campaignCode={campaignCode} />
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
                            Review the steps below to confirm your eligibility
                            and gather required documentation before you begin.
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
    location: PropTypes.shape({
        search: PropTypes.string.isRequired,
    }).isRequired,
    resetForm: PropTypes.func.isRequired,
    updateOsId: PropTypes.func.isRequired,
    osIdToClaim: PropTypes.string.isRequired,
    campaignCode: PropTypes.string.isRequired,
    campaignFlagActive: PropTypes.bool.isRequired,
    setCampaignCode: PropTypes.func.isRequired,
};

const mapStateToProps = (
    {
        auth: {
            user: { user },
        },
        claimForm: { osIdToClaim, formData: { campaign } = {} },
        featureFlags: { flags },
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
    campaignCode: campaign || '',
    campaignFlagActive: convertFeatureFlagsObjectToListOfActiveFlags(
        flags,
    ).includes(CLAIM_CAMPAIGNS),
});

export const mapDispatchToProps = dispatch => ({
    resetForm: () => dispatch(resetClaimForm()),
    updateOsId: osID => dispatch(updateOsIdToClaim(osID)),
    setCampaignCode: value =>
        dispatch(updateClaimFormField({ field: 'campaign', value })),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withRouter(withStyles(claimIntroStyles)(withScrollReset(ClaimIntro))));
