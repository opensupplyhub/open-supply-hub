/* eslint no-unused-vars: 0 */
import React, { useState, useEffect } from 'react';
import { func, object, shape, string, bool, oneOfType } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Switch from '@material-ui/core/Switch';
import RequiredAsterisk from '../../../../RequiredAsterisk';
import withScrollReset from '../../../HOCs/withScrollReset';
import contactInfoStepStyles from './styles';
import { EMPLOYMENT_VERIFICATION_OPTIONS } from './constants';
import {
    requiresUrlInput,
    requiresDocumentUpload,
    getUrlPlaceholder,
    getUrlLabel,
} from './utils';
import useVerificationMethodChange from './hooks';
import StyledSelect from '../../../../Filters/StyledSelect';
import { getSelectStyles } from '../../../../../util/util';
import ClaimAttachmentsUploader from '../../../../ClaimAttachmentsUploader';
import DialogTooltip from '../../../../Contribute/DialogTooltip';
import FormFieldTitle from '../../../Shared/FormFieldTitle.jsx/FormFieldTitle';
import findSelectedOption from '../utils';
import InputErrorText from '../../../../Contribute/InputErrorText';

const ContactInfoStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    updateFieldWithoutTouch,
    errors,
    touched,
    userEmail,
}) => {
    const isPublic = Boolean(formData.publicContactEnabled);
    const employmentOption = findSelectedOption(
        EMPLOYMENT_VERIFICATION_OPTIONS,
        formData.employmentVerification,
    );

    const [prevVerificationMethod, setPrevVerificationMethod] = useState(
        formData.employmentVerification || '',
    );

    // Update previous verification method when it changes.
    useEffect(() => {
        if (formData.employmentVerification !== prevVerificationMethod) {
            setPrevVerificationMethod(formData.companyAddressVerification);
        }
    }, [formData.employmentVerification]);

    // Clear verification URL and documents when verification method changes.
    useVerificationMethodChange(
        formData.employmentVerification,
        prevVerificationMethod,
        updateFieldWithoutTouch,
    );

    const selectedVerificationMethod = findSelectedOption(
        EMPLOYMENT_VERIFICATION_OPTIONS,
        formData.employmentVerification,
    );

    const showUrlInput = requiresUrlInput(selectedVerificationMethod?.value);
    const showDocumentUpload = requiresDocumentUpload(
        selectedVerificationMethod?.value,
    );

    // This checks if the employment verification field has been touched and either has validation errors
    // or no value selected
    const isEmploymentVerificationError = !!(
        touched?.employmentVerification && errors?.employmentVerification
    );

    // This checks if the employment verification URL field has been touched and has validation errors.
    const isEmploymentVerificationUrlError = !!(
        touched.employmentVerificationUrl && errors.employmentVerificationUrl
    );

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <div className={classes.accountInfoSection}>
                    <Typography className={classes.sectionTitle}>
                        Your Information (Claimant)
                    </Typography>
                    <Grid container spacing={16}>
                        <Grid item xs={12}>
                            <FormFieldTitle label="Your Email" required />
                            <TextField
                                fullWidth
                                value={userEmail || ''}
                                required
                                variant="outlined"
                                InputProps={{
                                    readOnly: true,
                                    classes: {
                                        root: classes.inputRoot,
                                        input: classes.input,
                                        notchedOutline: classes.notchedOutline,
                                    },
                                }}
                                className={classes.textField}
                                placeholder="opensupplyhubuser@company.com"
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormFieldTitle label="Your Name" required />
                            <TextField
                                fullWidth
                                required
                                name="claimantName"
                                value={formData.claimantName || ''}
                                onChange={e =>
                                    handleChange('claimantName', e.target.value)
                                }
                                onBlur={() => handleBlur('claimantName')}
                                variant="outlined"
                                error={
                                    touched.claimantName &&
                                    Boolean(errors.claimantName)
                                }
                                InputProps={{
                                    classes: {
                                        input: classes.inputStyles,
                                        notchedOutline:
                                            classes.notchedOutlineStyles,
                                    },
                                }}
                                placeholder="Enter your full name"
                            />
                            {touched.claimantName && errors.claimantName && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.claimantName}
                                    />
                                </div>
                            )}
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormFieldTitle label="Your Job Title" required />
                            <TextField
                                fullWidth
                                required
                                name="claimantTitle"
                                value={formData.claimantTitle || ''}
                                onChange={e =>
                                    handleChange(
                                        'claimantTitle',
                                        e.target.value,
                                    )
                                }
                                onBlur={() => handleBlur('claimantTitle')}
                                variant="outlined"
                                error={
                                    touched.claimantTitle &&
                                    Boolean(errors.claimantTitle)
                                }
                                InputProps={{
                                    classes: {
                                        input: `${classes.inputStyles}
                                        ${
                                            errors?.claimantTitle &&
                                            classes.errorStyle
                                        }`,
                                        notchedOutline:
                                            classes.notchedOutlineStyles,
                                    },
                                }}
                                placeholder="e.g., Plant Manager, Safety Director"
                            />
                            {touched.claimantTitle && errors.claimantTitle && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.claimantName}
                                    />
                                </div>
                            )}
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
                            Employment Verification <RequiredAsterisk />
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
                                onChange={valueObject =>
                                    handleChange(
                                        'employmentVerification',
                                        valueObject.label,
                                    )
                                }
                                styles={getSelectStyles(
                                    isEmploymentVerificationError,
                                )}
                                placeholder="Choose ONE"
                                isMulti={false}
                            />
                        </div>
                        {touched.employmentVerification &&
                            errors.employmentVerification && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={errors.employmentVerification}
                                    />
                                </div>
                            )}
                    </div>
                    {showUrlInput && (
                        <Grid container spacing={16}>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    required
                                    type="url"
                                    variant="outlined"
                                    name="employmentVerificationUrl"
                                    // label={getUrlLabel(
                                    //     formData.employmentVerification,
                                    // )}
                                    value={formData.employmentVerificationUrl}
                                    onChange={e =>
                                        handleChange(
                                            'employmentVerificationUrl',
                                            e.target.value,
                                        )
                                    }
                                    onBlur={() =>
                                        handleBlur('employmentVerificationUrl')
                                    }
                                    InputProps={{
                                        classes: {
                                            input: `${classes.inputStyles}
                                            ${
                                                errors?.employmentVerificationUrl &&
                                                classes.errorStyle
                                            }`,
                                            notchedOutline:
                                                classes.notchedOutlineStyles,
                                        },
                                    }}
                                    placeholder={getUrlPlaceholder(
                                        formData.employmentVerification,
                                    )}
                                    error={isEmploymentVerificationUrlError}
                                />
                                {touched.employmentVerificationUrl &&
                                    errors.employmentVerificationUrl && (
                                        <div
                                            className={classes.errorWrapStyles}
                                        >
                                            <InputErrorText
                                                text={
                                                    errors.employmentVerificationUrl
                                                }
                                            />
                                        </div>
                                    )}
                            </Grid>
                        </Grid>
                    )}
                    {showDocumentUpload && (
                        <Grid item xs={12} className={classes.gridSpacing}>
                            <ClaimAttachmentsUploader
                                inputId="employment-verification-upload"
                                title={
                                    'Upload your documents/photos\nPlease upload one or more clear photos or scans of your selected verification method. You can upload multiple files.'
                                }
                                files={
                                    formData.employmentVerificationDocuments ||
                                    []
                                }
                                updateUploadFiles={newFiles =>
                                    handleChange(
                                        'employmentVerificationDocuments',
                                        newFiles,
                                    )
                                }
                            />
                            {touched.employmentVerificationDocuments &&
                                errors.employmentVerificationDocuments && (
                                    <div className={classes.errorWrapStyles}>
                                        <InputErrorText
                                            text={
                                                errors.employmentVerificationDocuments
                                            }
                                        />
                                    </div>
                                )}
                        </Grid>
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
                                    onChange={(_, checked) => {
                                        handleChange(
                                            'publicContactEnabled',
                                            checked,
                                        );

                                        // When enabling public contact, prefill fields
                                        if (checked) {
                                            // Copy claimantName -> contactName if claimant has data
                                            const claimantHasName = Boolean(
                                                (formData.claimantName || '')
                                                    .toString()
                                                    .trim(),
                                            );
                                            if (claimantHasName) {
                                                handleChange(
                                                    'contactName',
                                                    formData.claimantName,
                                                );
                                            }

                                            // Always set contactEmail from userEmail; remains editable
                                            if (userEmail) {
                                                handleChange(
                                                    'contactEmail',
                                                    userEmail,
                                                );
                                            }
                                        }
                                    }}
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
                                    variant="outlined"
                                    error={
                                        touched.contactName &&
                                        Boolean(errors.contactName)
                                    }
                                    InputProps={{
                                        classes: {
                                            input: `${classes.inputStyles}`,
                                            notchedOutline:
                                                classes.notchedOutlineStyles,
                                        },
                                    }}
                                    placeholder="Contact person's name"
                                />
                                {touched.contactName && errors.contactName && (
                                    <div className={classes.errorWrapStyles}>
                                        <InputErrorText
                                            text={errors.contactName}
                                        />
                                    </div>
                                )}
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
                                    variant="outlined"
                                    InputProps={{
                                        classes: {
                                            input: classes.inputStyles,
                                            notchedOutline:
                                                classes.notchedOutlineStyles,
                                        },
                                    }}
                                    error={
                                        touched.contactEmail &&
                                        Boolean(errors.contactEmail)
                                    }
                                    placeholder="contact@company.com"
                                />
                                {touched.contactEmail && errors.contactEmail && (
                                    <div className={classes.errorWrapStyles}>
                                        <InputErrorText
                                            text={errors?.contactEmail}
                                        />
                                    </div>
                                )}
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
