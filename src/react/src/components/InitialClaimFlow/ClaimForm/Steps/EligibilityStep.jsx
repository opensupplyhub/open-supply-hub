/* eslint no-unused-vars: 0 */
import React, { useState } from 'react';
import { func, object, string } from 'prop-types';
import { connect } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import Security from '@material-ui/icons/Security';
import SecurityOutlinedIcon from '@material-ui/icons/SecurityOutlined';

import COLOURS from '../../../../util/COLOURS';
import withScrollReset from '../../HOCs/withScrollReset';
import StyledSelect from '../../../Filters/StyledSelect';
import { getSelectStyles } from '../../../../util/util';
import { mainRoute } from '../../../../util/constants';
import { eligibilityStepStyles } from '../styles';

const RELATIONSHIP_OPTIONS = [
    { value: 'owner', label: 'I am the owner of this production location' },
    {
        value: 'manager',
        label: 'I am a manager working at this production location',
    },
    {
        value: 'parent_company_owner_or_manager',
        label: 'I represent the parent company that owns/manages this facility',
    },
    {
        value: 'worker',
        label:
            "I work here but don't have management authority (will require supervisor verification)",
    },
    {
        value: 'partner',
        label: 'I am a buyer, supplier, agent, or other business partner',
    },
    {
        value: 'other',
        label: 'Other relationship',
    },
];

const EligibilityStep = ({
    classes,
    formData,
    handleChange,
    onNext,
    onBack,
    userEmail,
    organizationName,
}) => {
    const history = useHistory();
    const [relationshipTouched, setRelationshipTouched] = useState(false);
    const [ineligibleDialogOpen, setIneligibleDialogOpen] = useState(false);

    const selectedRelationship = formData.relationship || null;

    const isRelationshipError = relationshipTouched && !selectedRelationship;
    const isFormValid = !!selectedRelationship;

    const handleCloseIneligibleDialog = () => {
        setIneligibleDialogOpen(false);
        handleChange('relationship', null);
        setRelationshipTouched(false);
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
                            value={selectedRelationship}
                            onChange={value => {
                                if (
                                    value &&
                                    (value.value === 'partner' ||
                                        value.value === 'other')
                                ) {
                                    setIneligibleDialogOpen(true);
                                } else {
                                    handleChange('relationship', value);
                                    setRelationshipTouched(true);
                                }
                            }}
                            onBlur={() => setRelationshipTouched(true)}
                            styles={getSelectStyles(isRelationshipError)}
                            placeholder="Select your relationship to this production location"
                            isMulti={false}
                        />
                    </div>
                </div>
            </Grid>

            <Dialog open={ineligibleDialogOpen}>
                <DialogTitle style={{ textAlign: 'center' }}>
                    Not Eligible to File Claim
                </DialogTitle>
                <DialogContent>
                    <Typography
                        variant="body1"
                        style={{ textAlign: 'center', fontSize: '16px' }}
                    >
                        You are not eligible to file a claim for this location.
                        Only the owner, manager, authorized employee, or a
                        parent company representative of the production location
                        can submit a claim. Please ask the production location
                        to claim directly.
                    </Typography>
                </DialogContent>
                <DialogActions style={{ justifyContent: 'center' }}>
                    <Button
                        variant="outlined"
                        color="primary"
                        onClick={handleGoToMainPage}
                    >
                        Back to Open Supply Hub
                    </Button>
                    <Button
                        variant="outlined"
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
    onNext: () => {},
    onBack: () => {},
};

EligibilityStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    handleBlur: func.isRequired,
    errors: object,
    touched: object,
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
