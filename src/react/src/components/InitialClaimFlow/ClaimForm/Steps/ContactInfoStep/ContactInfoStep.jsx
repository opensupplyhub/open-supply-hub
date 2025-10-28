import React from 'react';
import { func, object, shape, string, bool, oneOfType } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Switch from '@material-ui/core/Switch';

import withScrollReset from '../../../HOCs/withScrollReset';
import contactInfoStepStyles from './styles';
import EMPLOYMENT_VERIFICATION_OPTIONS from './constants';
import StyledSelect from '../../../../Filters/StyledSelect';
import { getSelectStyles } from '../../../../../util/util';
import ClaimAttachmentsUploader from '../../../../ClaimAttachmentsUploader';
import DialogTooltip from '../../../../Contribute/DialogTooltip';

const ContactInfoStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    errors,
    touched,
    userEmail,
}) => {
    const isPublic = Boolean(formData.publicContactEnabled);
    const employmentOption = formData.employmentVerification || null;
    const employmentError = Boolean(
        touched?.employmentVerification &&
            (errors?.employmentVerification || !employmentOption),
    );
    const showUploadBlock = Boolean(
        employmentOption &&
            employmentOption.value !== 'company_website' &&
            employmentOption.value !== 'linkedin_page',
    );
    const showWebsiteUrlField = employmentOption?.value === 'company_website';
    const showLinkedInUrlField = employmentOption?.value === 'linkedin_page';

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <div className={classes.accountInfoSection}>
                    <Typography className={classes.sectionTitle}>
                        Your Information (Claimant)
                    </Typography>
                    <Grid container spacing={16}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Your Email"
                                value={userEmail || ''}
                                required
                                InputProps={{ readOnly: true }}
                                className={classes.textField}
                                placeholder="opensupplyhubuser@company.com"
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                required
                                name="claimantName"
                                label="Your Name"
                                value={formData.claimantName || ''}
                                onChange={e =>
                                    handleChange('claimantName', e.target.value)
                                }
                                onBlur={() => handleBlur('claimantName')}
                                className={classes.textField}
                                placeholder="Enter your full name"
                                error={
                                    touched?.claimantName &&
                                    Boolean(errors?.claimantName)
                                }
                                helperText={
                                    touched?.claimantName &&
                                    errors?.claimantName
                                }
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                required
                                name="claimantTitle"
                                label="Your Job Title"
                                value={formData.claimantTitle || ''}
                                onChange={e =>
                                    handleChange(
                                        'claimantTitle',
                                        e.target.value,
                                    )
                                }
                                onBlur={() => handleBlur('claimantTitle')}
                                className={classes.textField}
                                placeholder="e.g., Plant Manager, Safety Director"
                                error={
                                    touched?.claimantTitle &&
                                    Boolean(errors?.claimantTitle)
                                }
                                helperText={
                                    touched?.claimantTitle &&
                                    errors?.claimantTitle
                                }
                            />
                        </Grid>
                    </Grid>

                    <div className={classes.infoAlert}>
                        <div className={classes.infoAlertInner}>
                            <Typography variant="caption">
                                <strong>IMPORTANT!</strong> Your name and job
                                title must match the person associated with the
                                email address provided above.
                            </Typography>
                        </div>
                    </div>

                    <div className={classes.gridSpacing}>
                        <Typography className={classes.sectionTitle}>
                            Employment Verification*
                        </Typography>
                        <Typography className={classes.helperTextSmall}>
                            You need to select and provide one of the below
                            items for employment verification.
                        </Typography>
                        <div className={classes.selectWrapper}>
                            <StyledSelect
                                id="employmentVerification"
                                name="employmentVerification"
                                aria-label="Select employment verification option"
                                label={null}
                                options={EMPLOYMENT_VERIFICATION_OPTIONS}
                                onBlur={() =>
                                    handleBlur('employmentVerification')
                                }
                                value={employmentOption}
                                onChange={value =>
                                    handleChange(
                                        'employmentVerification',
                                        value,
                                    )
                                }
                                styles={getSelectStyles(employmentError)}
                                placeholder="Choose ONE"
                                isMulti={false}
                            />
                        </div>
                    </div>

                    {showUploadBlock && (
                        <div className={classes.gridSpacing}>
                            <ClaimAttachmentsUploader
                                inputId="employment-verification-upload"
                                title={
                                    'Upload your documents/photos\nPlease upload one or more clear photos or scans of your selected verification method. You can upload multiple files.'
                                }
                                files={
                                    formData.employmentVerificationFiles || []
                                }
                                updateUploadFiles={newFiles =>
                                    handleChange(
                                        'employmentVerificationFiles',
                                        newFiles,
                                    )
                                }
                            />
                        </div>
                    )}

                    {showWebsiteUrlField && (
                        <div className={classes.gridSpacing}>
                            <TextField
                                fullWidth
                                required
                                type="url"
                                name="employmentVerificationUrl"
                                label="Website URL"
                                value={formData.employmentVerificationUrl || ''}
                                onChange={e =>
                                    handleChange(
                                        'employmentVerificationUrl',
                                        e.target.value,
                                    )
                                }
                                onBlur={() =>
                                    handleBlur('employmentVerificationUrl')
                                }
                                className={classes.textField}
                                placeholder="https://example.com/team"
                                error={
                                    touched?.employmentVerificationUrl &&
                                    Boolean(errors?.employmentVerificationUrl)
                                }
                                helperText={
                                    touched?.employmentVerificationUrl &&
                                    errors?.employmentVerificationUrl
                                }
                            />
                        </div>
                    )}

                    {showLinkedInUrlField && (
                        <div className={classes.gridSpacing}>
                            <TextField
                                fullWidth
                                required
                                type="url"
                                name="employmentVerificationUrl"
                                label="LinkedIn Profile URL"
                                value={formData.employmentVerificationUrl || ''}
                                onChange={e =>
                                    handleChange(
                                        'employmentVerificationUrl',
                                        e.target.value,
                                    )
                                }
                                onBlur={() =>
                                    handleBlur('employmentVerificationUrl')
                                }
                                className={classes.textField}
                                placeholder="https://linkedin.com/in/yourprofile"
                                error={
                                    touched?.employmentVerificationUrl &&
                                    Boolean(errors?.employmentVerificationUrl)
                                }
                                helperText={
                                    touched?.employmentVerificationUrl &&
                                    errors?.employmentVerificationUrl
                                }
                            />
                        </div>
                    )}

                    <Typography className={classes.sectionTitle}>
                        Production Location Contact Person
                    </Typography>
                    <div className={classes.publicContactBox}>
                        <div className={classes.publicContactRow}>
                            <div>
                                <Typography variant="subtitle1">
                                    Do you want this location&apos;s contact
                                    info to be public?
                                </Typography>
                                <Typography className={classes.helperTextSmall}>
                                    Toggle &quot;Yes&quot; to add public contact
                                    details. When enabled, contact info will be
                                    visible on your Open Supply Hub profile for
                                    sourcing requests, general inquiries, and
                                    potential business opportunities.
                                </Typography>
                            </div>
                            <div>
                                <Switch
                                    checked={isPublic}
                                    onChange={(_, checked) =>
                                        handleChange(
                                            'publicContactEnabled',
                                            checked,
                                        )
                                    }
                                    color="primary"
                                />
                            </div>
                        </div>
                    </div>

                    {isPublic && (
                        <Grid
                            container
                            spacing={16}
                            className={classes.gridSpacing}
                        >
                            <Grid item xs={12} sm={6}>
                                <div className={classes.labelRow}>
                                    <span className={classes.fieldLabel}>
                                        Contact Name
                                    </span>
                                    <DialogTooltip
                                        text={
                                            "We're making a Premium package for connecting with customers and growing your business. Beta fields preview part of this package and currently appear on your profile. Once the new package is live, you'll get details on keeping those fields active."
                                        }
                                        childComponent={
                                            <span className={classes.betaBadge}>
                                                BETA
                                            </span>
                                        }
                                    />
                                </div>
                                <TextField
                                    fullWidth
                                    name="contactName"
                                    value={formData.contactName || ''}
                                    onChange={e =>
                                        handleChange(
                                            'contactName',
                                            e.target.value,
                                        )
                                    }
                                    onBlur={() => handleBlur('contactName')}
                                    className={classes.textField}
                                    placeholder="Contact person's name"
                                    error={
                                        touched?.contactName &&
                                        Boolean(errors?.contactName)
                                    }
                                    helperText={
                                        touched?.contactName &&
                                        errors?.contactName
                                    }
                                />
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <div className={classes.labelRow}>
                                    <span className={classes.fieldLabel}>
                                        Contact Email
                                    </span>
                                    <DialogTooltip
                                        text={
                                            "We're making a Premium package for connecting with customers and growing your business. Beta fields preview part of this package and currently appear on your profile. Once the new package is live, you'll get details on keeping those fields active."
                                        }
                                        childComponent={
                                            <span className={classes.betaBadge}>
                                                BETA
                                            </span>
                                        }
                                    />
                                </div>
                                <TextField
                                    fullWidth
                                    type="email"
                                    name="contactEmail"
                                    value={formData.contactEmail || ''}
                                    onChange={e =>
                                        handleChange(
                                            'contactEmail',
                                            e.target.value,
                                        )
                                    }
                                    onBlur={() => handleBlur('contactEmail')}
                                    className={classes.textField}
                                    placeholder="contact@company.com"
                                    error={
                                        touched?.contactEmail &&
                                        Boolean(errors?.contactEmail)
                                    }
                                    helperText={
                                        touched?.contactEmail &&
                                        errors?.contactEmail
                                    }
                                />
                            </Grid>
                        </Grid>
                    )}
                </div>
            </Grid>
        </Grid>
    );
};

ContactInfoStep.defaultProps = {
    userEmail: null,
    errors: {},
    touched: {},
};

ContactInfoStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    handleBlur: func.isRequired,
    errors: shape({
        claimantName: oneOfType([string, object]),
        claimantTitle: oneOfType([string, object]),
        contactEmail: oneOfType([string, object]),
        contactName: oneOfType([string, object]),
    }),
    touched: shape({
        claimantName: bool,
        claimantTitle: bool,
        contactEmail: bool,
        contactName: bool,
    }),
    userEmail: string,
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
    withStyles(contactInfoStepStyles)(withScrollReset(ContactInfoStep)),
);
