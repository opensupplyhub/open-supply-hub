import React, { useState } from 'react';
import { func, object, string, shape, bool, oneOfType } from 'prop-types';
import { connect } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';

import withScrollReset from '../../../HOCs/withScrollReset';
import StyledSelect from '../../../../Filters/StyledSelect';
import { getSelectStyles } from '../../../../../util/util';
import { mainRoute } from '../../../../../util/constants';
import eligibilityStepStyles from './styles';
import RELATIONSHIP_OPTIONS from './constants';
import InputErrorText from '../../../../Contribute/InputErrorText';
import findSelectedOption from '../utils';

const EligibilityStep = ({
    classes,
    formData,
    handleChange,
    errors,
    touched,
    userEmail,
    organizationName,
    handleBlur,
}) => {
    const history = useHistory();
    const [ineligibleDialogOpen, setIneligibleDialogOpen] = useState(false);

    const selectedRelationship = findSelectedOption(
        RELATIONSHIP_OPTIONS,
        formData.relationship,
    );

    // This checks if the relationship field has been touched and either has validation errors
    // or no value selected
    const isRelationshipError = !!(
        touched?.relationship && errors?.relationship
    );

    const handleCloseIneligibleDialog = () => {
        // Close dialog without altering previously selected valid relationship.
        setIneligibleDialogOpen(false);
    };

    const handleGoToMainPage = () => {
        history.push(mainRoute);
    };

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <div className={classes.accountInfoSection}>
                    <div className={classes.accountInfoBox}>
                        <div className={classes.accountInfoRow}>
                            <span className={classes.accountInfoLabel}>
                                Account email:
                            </span>
                            <span className={classes.accountInfoValue}>
                                {userEmail || 'Not available'}
                            </span>
                        </div>
                        <div className={classes.accountInfoRow}>
                            <span className={classes.accountInfoLabel}>
                                Organization name:
                            </span>
                            <span className={classes.accountInfoValue}>
                                {organizationName || 'Not available'}
                            </span>
                        </div>
                    </div>

                    <Typography className={classes.sectionTitle}>
                        Select your relationship to this production location:
                    </Typography>
                    <div className={classes.selectWrapper}>
                        <StyledSelect
                            id="relationship"
                            name="relationship"
                            aria-label="Select your relationship to this production location"
                            label={null}
                            options={RELATIONSHIP_OPTIONS}
                            onBlur={() => handleBlur('relationship')}
                            value={selectedRelationship}
                            onChange={valueObject => {
                                if (
                                    valueObject &&
                                    (valueObject.value === 'partner' ||
                                        valueObject.value === 'other')
                                ) {
                                    setIneligibleDialogOpen(true);
                                } else {
                                    handleChange(
                                        'relationship',
                                        valueObject.label,
                                    );
                                }
                            }}
                            styles={getSelectStyles(isRelationshipError)}
                            placeholder="Select your relationship to this production location"
                            isMulti={false}
                        />
                    </div>
                    {touched.relationship && errors.relationship && (
                        <div className={classes.errorWrapStyles}>
                            <InputErrorText text={errors.relationship} />
                        </div>
                    )}
                </div>
            </Grid>

            <Dialog open={ineligibleDialogOpen}>
                <DialogTitle className={classes.dialogTitle}>
                    Not Eligible to File Claim
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
                        variant="contained"
                        color="primary"
                        onClick={handleGoToMainPage}
                    >
                        Back to Open Supply Hub
                    </Button>
                    <Button
                        variant="contained"
                        color="secondary"
                        onClick={handleCloseIneligibleDialog}
                    >
                        Return to Claims
                    </Button>
                </DialogActions>
            </Dialog>
        </Grid>
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
}) => ({
    userEmail: user?.email,
    organizationName: user?.name,
});

export default connect(mapStateToProps)(
    withStyles(eligibilityStepStyles)(withScrollReset(EligibilityStep)),
);
