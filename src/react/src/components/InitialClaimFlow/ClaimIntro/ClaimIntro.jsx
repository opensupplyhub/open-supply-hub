import React, { useEffect, useRef, useState } from 'react';
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
import { rememberClaimInviteCode } from '../../../util/claimInvite';
import {
    forgetClaimCampaignCode,
    getClaimCampaignCode,
    isActiveClaimCampaign,
    normalizeCampaignCode,
    rememberClaimCampaignCode,
} from '../../../util/claimCampaign';

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

    // A claim invite link carries ?invite=<code>. Remember it before the
    // sign-in check: the query string doesn't survive logging in or
    // registering, and the code goes out with the claim.
    useEffect(() => {
        rememberClaimInviteCode(osID, location.search);
    }, [osID, location.search]);
    // Read inside the effect below without making it a dependency: the
    // effect sets the code itself, and must not run (and look it up)
    // again because of that.
    const campaignCodeRef = useRef(campaignCode);
    campaignCodeRef.current = campaignCode;
    // The code the backend confirmed as an active campaign on this visit.
    // Only this one shows in the banner: a code already in the form (from
    // an earlier visit, or a previous link) stays hidden until the lookup
    // for the current link says it's valid, and an invalid one never shows.
    const [confirmedCampaignCode, setConfirmedCampaignCode] = useState('');

    // A claims campaign link carries ?campaign=<code>. Like the invite
    // code, it is remembered per OS ID before the sign-in check, so it
    // survives logging in and the claim form's Back button (both reopen
    // this page without the query string). The code only goes into the
    // form, and the banner only shows, once the backend confirms it
    // belongs to an active campaign.
    useEffect(() => {
        // Nothing is confirmed for this link until the lookup says so.
        setConfirmedCampaignCode('');

        const clearCampaignCode = () => {
            if (campaignCodeRef.current) {
                setCampaignCode('');
            }
        };

        if (!campaignFlagActive) {
            clearCampaignCode();
            return undefined;
        }

        const params = new URLSearchParams(location.search);
        if (params.has('campaign')) {
            const fromLink = normalizeCampaignCode(params.get('campaign'));
            if (!fromLink) {
                // A malformed code replaces (and so drops) any earlier one.
                forgetClaimCampaignCode(osID);
                clearCampaignCode();
                return undefined;
            }
            rememberClaimCampaignCode(osID, fromLink);
        }

        // The lookup needs a signed-in user; the code waits in storage.
        if (!userHasSignedIn) {
            return undefined;
        }

        const code = getClaimCampaignCode(osID);
        if (!code) {
            // Nothing remembered (or it lapsed): clear a stale form code.
            clearCampaignCode();
            return undefined;
        }

        let cancelled = false;
        isActiveClaimCampaign(code).then(active => {
            if (cancelled) {
                return;
            }
            if (active) {
                setCampaignCode(code);
                setConfirmedCampaignCode(code);
                return;
            }
            if (active === false) {
                // Unknown or closed campaign: stop sending it.
                forgetClaimCampaignCode(osID);
            }
            // On a failed lookup the code stays remembered (the claim
            // still sends it), but no banner is shown.
            clearCampaignCode();
        });
        return () => {
            cancelled = true;
        };
    }, [
        osID,
        location.search,
        campaignFlagActive,
        userHasSignedIn,
        setCampaignCode,
    ]);

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
                    <ClaimCampaignBanner campaignCode={confirmedCampaignCode} />
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
                        <Typography
                            variant="subheading"
                            className={classes.approvalTip}
                        >
                            Claims with a work email and an official document
                            are approved fastest.
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
        search: PropTypes.string,
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
