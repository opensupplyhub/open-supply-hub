import React, { useState } from 'react';
import { func, object, string, shape, bool, oneOfType } from 'prop-types';
import { connect } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';

import withScrollReset from '../../../HOCs/withScrollReset';
import StyledSelect from '../../../../Filters/StyledSelect';
import {
    convertFeatureFlagsObjectToListOfActiveFlags,
    getSelectStyles,
} from '../../../../../util/util';
import {
    mapRoute,
    RELAXED_CLAIM_ELIGIBILITY,
} from '../../../../../util/constants';
import eligibilityStepStyles from './styles';
import RELATIONSHIP_OPTIONS, { RELAXED_WORKER_LABEL } from './constants';
import InputErrorText from '../../../../Contribute/InputErrorText';
import findSelectedOption from '../utils';
import FormFieldTitle from '../../../Shared/FormFieldTitle/FormFieldTitle';
import { selectStyles } from '../../styles';

const EligibilityStep = ({
    classes,
    formData,
    handleChange,
    errors,
    touched,
    userEmail,
    organizationName,
    handleBlur,
    isRelaxedEligibility,
}) => {
    const history = useHistory();
    const [ineligibleDialogOpen, setIneligibleDialogOpen] = useState(false);

    // Accept either the canonical label or the relaxed one (a pending
    // claim saved while the switch was on), then show the current label
    // for that value.
    const storedOption = findSelectedOption(
        [
            ...RELATIONSHIP_OPTIONS,
            { value: 'worker', label: RELAXED_WORKER_LABEL },
        ],
        formData.claimantLocationRelationship,
    );

    // Relaxed policy (relaxed_claim_eligibility switch): employees are
    // directly eligible, so the worker option drops its
    // supervisor-verification caveat and the manager option goes away —
    // managers are employees, so under the relaxed policy the two
    // options were the same answer twice. A pending claim saved with
    // "manager" while the switch was off keeps its option (the stored
    // answer stays valid and visible; only new picks are constrained).
    // The stored claimant_location_relationship is whichever label the
    // claimant saw and picked; findSelectedOption above accepts both
    // generations of the worker label, so stored values round-trip
    // whichever way the switch is set when the claim is reopened.
    const relationshipOptions = RELATIONSHIP_OPTIONS.filter(
        option =>
            !(
                isRelaxedEligibility &&
                option.value === 'manager' &&
                storedOption?.value !== 'manager'
            ),
    ).map(option =>
        option.value === 'worker' && isRelaxedEligibility
            ? { ...option, label: RELAXED_WORKER_LABEL }
            : option,
    );

    const selectedRelationship = storedOption
        ? relationshipOptions.find(
              option => option.value === storedOption.value,
          ) || null
        : null;

    // This checks if the relationship field has been touched and either has validation errors
    // or no value selected
    const isRelationshipError = !!(
        touched?.claimantLocationRelationship &&
        errors?.claimantLocationRelationship
    );

    const handleCloseIneligibleDialog = () => {
        // Close dialog without altering previously selected valid relationship.
        setIneligibleDialogOpen(false);
    };

    const handleGoToMainPage = () => {
        history.push(mapRoute);
    };

    return (
        <div className={classes.eligibilityStepContainer}>
            <div className={classes.accountInfoSection}>
                <Typography component="h3" className={classes.sectionHeading}>
                    Account Information
                </Typography>
                <div className={classes.accountInfoBox}>
                    <div className={classes.accountInfoRow}>
                        <span className={classes.accountInfoLabel}>
                            Organization:
                        </span>
                        <span className={classes.accountInfoValue}>
                            {organizationName || 'Not available'}
                        </span>
                    </div>
                    <div className={classes.accountInfoRow}>
                        <span className={classes.accountInfoLabel}>
                            Email address:
                        </span>
                        <span className={classes.accountInfoValue}>
                            {userEmail || 'Not available'}
                        </span>
                    </div>
                </div>
            </div>

            <FormFieldTitle
                label="Your Relationship to this Production Location"
                classes={{ title: classes.sectionTitleRequired }}
                required
            />
            <div className={classes.selectWrapper}>
                <StyledSelect
                    id="claimantLocationRelationship"
                    name="claimantLocationRelationship"
                    aria-label="Select your relationship to this production location"
                    label={null}
                    options={relationshipOptions}
                    onBlur={() => handleBlur('claimantLocationRelationship')}
                    value={selectedRelationship}
                    onChange={valueObject => {
                        if (
                            valueObject &&
                            (valueObject.value === 'partner' ||
                                valueObject.value === 'other')
                        ) {
                            setIneligibleDialogOpen(true);
                        } else {
                            // Store the label the claimant actually saw
                            // and chose: the stored string is claimant
                            // data (claim history, admin, exports), so
                            // it must never assert the supervisor-
                            // verification caveat to someone who picked
                            // the relaxed employee option.
                            handleChange(
                                'claimantLocationRelationship',
                                valueObject.label,
                            );
                        }
                    }}
                    styles={getSelectStyles(isRelationshipError, selectStyles)}
                    placeholder="Select your relationship to this production location"
                    isMulti={false}
                />
            </div>
            {touched.claimantLocationRelationship &&
                errors.claimantLocationRelationship && (
                    <div className={classes.errorWrapStyles}>
                        <InputErrorText
                            text={errors.claimantLocationRelationship}
                        />
                    </div>
                )}

            <Dialog open={ineligibleDialogOpen}>
                <DialogTitle className={classes.dialogTitle}>
                    <Typography component="h3" className={classes.dialogTitle}>
                        Not Eligible to File Claim
                    </Typography>
                </DialogTitle>
                <DialogContent>
                    <Typography
                        variant="body1"
                        className={classes.dialogBodyText}
                    >
                        You are not eligible to file a claim for this location.
                        Only the owner, manager, authorized employee, or a
                        parent company representative of the production location
                        can submit a claim. Please ask the production location
                        to claim directly.
                    </Typography>
                </DialogContent>
                <DialogActions className={classes.dialogActions}>
                    <Button
                        variant="outlined"
                        onClick={handleGoToMainPage}
                        className={classes.backButton}
                    >
                        Go Back to Open Supply Hub
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleCloseIneligibleDialog}
                        className={classes.continueButton}
                    >
                        Continue to Claim
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
};

EligibilityStep.defaultProps = {
    userEmail: null,
    organizationName: null,
};

EligibilityStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    handleBlur: func.isRequired,
    errors: shape({
        relationship: oneOfType([string, object]),
    }).isRequired,
    touched: shape({
        relationship: bool,
    }).isRequired,
    userEmail: string,
    organizationName: string,
};

const mapStateToProps = ({
    auth: {
        user: { user },
    },
    featureFlags: { flags },
}) => ({
    userEmail: user?.email,
    organizationName: user?.name,
    isRelaxedEligibility: convertFeatureFlagsObjectToListOfActiveFlags(
        flags,
    ).includes(RELAXED_CLAIM_ELIGIBILITY),
});

export default connect(mapStateToProps)(
    withStyles(eligibilityStepStyles)(withScrollReset(EligibilityStep)),
);
