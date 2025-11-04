import React, { useState, useEffect } from 'react';
import {
    func,
    object,
    shape,
    string,
    bool,
    oneOfType,
    array,
} from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Switch from '@material-ui/core/Switch';
import Warning from '@material-ui/icons/Warning';
import withScrollReset from '../../../HOCs/withScrollReset';
import contactInfoStepStyles from './styles';
import { EMPLOYMENT_VERIFICATION_OPTIONS } from './constants';
import {
    requiresUrlInput,
    requiresDocumentUpload,
    getUrlPlaceholder,
} from './utils';
import useVerificationMethodChange from './hooks';
import StyledSelect from '../../../../Filters/StyledSelect';
import { getSelectStyles } from '../../../../../util/util';
import ClaimAttachmentsUploader from '../../../../ClaimAttachmentsUploader';
import DialogTooltip from '../../../../Contribute/DialogTooltip';
import FormFieldTitle from '../../../Shared/FormFieldTitle.jsx/FormFieldTitle';
import findSelectedOption from '../utils';
import InputErrorText from '../../../../Contribute/InputErrorText';
import { selectStyles } from '../../styles';

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
    const isPublic = Boolean(formData.pointOfContactPubliclyVisible);
    const employmentOption = findSelectedOption(
        EMPLOYMENT_VERIFICATION_OPTIONS,
        formData.claimantEmploymentVerificationMethod,
    );

    const [prevVerificationMethod, setPrevVerificationMethod] = useState(
        formData.claimantEmploymentVerificationMethod || '',
    );

    // Update previous verification method when it changes.
    useEffect(() => {
        if (
            formData.claimantEmploymentVerificationMethod !==
            prevVerificationMethod
        ) {
            setPrevVerificationMethod(
                formData.claimantEmploymentVerificationMethod,
            );
        }
    }, [formData.claimantEmploymentVerificationMethod]);

    // Clear verification URL and documents when verification method changes.
    useVerificationMethodChange(
        formData.claimantEmploymentVerificationMethod,
        prevVerificationMethod,
        updateFieldWithoutTouch,
    );

    const selectedVerificationMethod = findSelectedOption(
        EMPLOYMENT_VERIFICATION_OPTIONS,
        formData.claimantEmploymentVerificationMethod,
    );

    const showUrlInput = requiresUrlInput(selectedVerificationMethod?.value);
    const showDocumentUpload = requiresDocumentUpload(
        selectedVerificationMethod?.value,
    );

    // This checks if the employment verification field has been touched and either has validation errors
    // or no value selected.
    const isEmploymentVerificationError = !!(
        touched?.claimantEmploymentVerificationMethod &&
        errors?.claimantEmploymentVerificationMethod
    );

    // This checks if the employment verification URL field has been touched and has validation errors.
    let urlFieldName = null;
    if (selectedVerificationMethod?.value === 'linkedin-page') {
        urlFieldName = 'claimantLinkedinProfileUrl';
    } else if (
        selectedVerificationMethod?.value === 'company-website-address'
    ) {
        urlFieldName = 'yourBusinessWebsite';
    }

    const isEmploymentVerificationUrlError = !!(
        urlFieldName &&
        touched[urlFieldName] &&
        errors[urlFieldName]
    );

    return (
        <Grid container>
            <Grid item>
                <div className={classes.fieldContainer}>
                    <FormFieldTitle
                        label="Your Email"
                        classes={{ title: classes.formLabelRoot }}
                        required
                    />
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
                                notchedOutline: classes.notchedOutlineStyles,
                            },
                        }}
                        className={classes.textField}
                        placeholder="opensupplyhubuser@company.com"
                    />
                </div>
                <div className={classes.fieldContainer}>
                    <FormFieldTitle
                        label="Your Name"
                        required
                        classes={{ title: classes.formLabel }}
                    />
                    <TextField
                        fullWidth
                        required
                        name="yourName"
                        value={formData.yourName || ''}
                        onChange={e => handleChange('yourName', e.target.value)}
                        onBlur={() => handleBlur('yourName')}
                        variant="outlined"
                        error={touched.yourName && Boolean(errors.yourName)}
                        InputProps={{
                            classes: {
                                input: classes.inputStyles,
                                notchedOutline: classes.notchedOutlineStyles,
                            },
                        }}
                        placeholder="Enter your full name"
                    />
                    {touched.yourName && errors.yourName && (
                        <div className={classes.errorWrapStyles}>
                            <InputErrorText text={errors.yourName} />
                        </div>
                    )}
                </div>
                <div className={classes.fieldContainer}>
                    <FormFieldTitle
                        label="Your Job Title"
                        classes={{ title: classes.formLabel }}
                        required
                    />
                    <TextField
                        fullWidth
                        required
                        name="yourTitle"
                        value={formData.yourTitle || ''}
                        onChange={e =>
                            handleChange('yourTitle', e.target.value)
                        }
                        onBlur={() => handleBlur('yourTitle')}
                        variant="outlined"
                        error={touched.yourTitle && Boolean(errors.yourTitle)}
                        InputProps={{
                            classes: {
                                input: `${classes.inputStyles}`,
                                notchedOutline: classes.notchedOutlineStyles,
                            },
                        }}
                        placeholder="e.g., Plant Manager, Safety Director"
                    />
                    {touched.yourTitle && errors.yourTitle && (
                        <div className={classes.errorWrapStyles}>
                            <InputErrorText text={errors.yourTitle} />
                        </div>
                    )}
                </div>
                <div className={`${classes.boxWarningContainer}`}>
                    <Typography
                        variant="body2"
                        className={classes.boxWarningText}
                    >
                        <span className={classes.boxWarningTextIcon}>
                            <Warning className={classes.warningIcon} />
                            <strong>IMPORTANT!</strong>
                        </span>
                        <span>
                            &nbsp;Your name and job title must match the person
                            associated with the email address provided above.
                        </span>
                    </Typography>
                </div>
                <div className={classes.fieldContainer}>
                    <FormFieldTitle
                        label="Employment Verification"
                        classes={{ title: classes.formLabel }}
                        required
                    />
                    <StyledSelect
                        id="claimantEmploymentVerificationMethod"
                        name="claimantEmploymentVerificationMethod"
                        aria-label="Select employment verification option"
                        label={null}
                        options={EMPLOYMENT_VERIFICATION_OPTIONS}
                        onBlur={() =>
                            handleBlur('claimantEmploymentVerificationMethod')
                        }
                        value={employmentOption}
                        onChange={valueObject =>
                            handleChange(
                                'claimantEmploymentVerificationMethod',
                                valueObject.label,
                            )
                        }
                        styles={getSelectStyles(
                            isEmploymentVerificationError,
                            selectStyles,
                        )}
                        placeholder="You need to provide one of the below items for employment verification"
                        isMulti={false}
                    />
                    {touched.claimantEmploymentVerificationMethod &&
                        errors.claimantEmploymentVerificationMethod && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={
                                        errors.claimantEmploymentVerificationMethod
                                    }
                                />
                            </div>
                        )}
                </div>
                <div className={classes.fieldContainer}>
                    {showUrlInput && (
                        <FormFieldTitle
                            label="Website URL"
                            classes={{ title: classes.formLabel }}
                            required
                        />
                    )}
                    {showUrlInput && (
                        <TextField
                            fullWidth
                            required
                            type="url"
                            variant="outlined"
                            name={urlFieldName}
                            value={
                                (urlFieldName && formData[urlFieldName]) || ''
                            }
                            onChange={e =>
                                handleChange(urlFieldName, e.target.value)
                            }
                            onBlur={() => handleBlur(urlFieldName)}
                            InputProps={{
                                classes: {
                                    input: `${classes.inputStyles}`,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            placeholder={getUrlPlaceholder(
                                formData.claimantEmploymentVerificationMethod,
                            )}
                            error={isEmploymentVerificationUrlError}
                        />
                    )}
                    {showUrlInput &&
                        urlFieldName &&
                        touched[urlFieldName] &&
                        errors[urlFieldName] && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText text={errors[urlFieldName]} />
                            </div>
                        )}
                </div>
                <div>
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
                </div>
                <hr className={classes.separator} />

                <div className={classes.sectionContainer}>
                    <div className={classes.sectionTitleContainer}>
                        <Typography
                            variant="title"
                            component="h3"
                            className={classes.sectionTitle}
                        >
                            Do you want this location&apos;s contact info to be
                            public?
                        </Typography>
                        <div className={classes.switchContainer}>
                            <Switch
                                checked={isPublic}
                                onChange={(_, checked) => {
                                    handleChange(
                                        'pointOfContactPubliclyVisible',
                                        checked,
                                    );

                                    // When enabling public contact, prefill fields.
                                    if (checked) {
                                        // Copy yourName -> contactName if claimant has data.
                                        const claimantHasName = Boolean(
                                            (formData.yourName || '')
                                                .toString()
                                                .trim(),
                                        );
                                        if (claimantHasName) {
                                            handleChange(
                                                'pointOfContactPersonName',
                                                formData.yourName,
                                            );
                                        }

                                        // Always set contactEmail from userEmail; remains editable.
                                        if (userEmail) {
                                            handleChange(
                                                'pointOfContactEmail',
                                                userEmail,
                                            );
                                        }
                                    }
                                }}
                                color="primary"
                            />
                        </div>
                    </div>
                    <Typography className={classes.sectionDescription}>
                        Toggle &quot;Yes&quot; to add public contact details.
                        When enabled, contact info will be visible on your Open
                        Supply Hub profile for sourcing requests, general
                        inquiries, and potential business opportunities.
                    </Typography>
                </div>
                <div className={classes.fieldContainer}>
                    {isPublic && (
                        <DialogTooltip
                            text={
                                "We're making a Premium package for connecting with customers and growing your business. Beta fields preview part of this package and currently appear on your profile. Once the new package is live, you'll get details on keeping those fields active."
                            }
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    )}
                    {isPublic && (
                        <FormFieldTitle
                            label="Contact Name"
                            classes={{ title: classes.formLabel }}
                            required
                        />
                    )}

                    {isPublic && (
                        <TextField
                            fullWidth
                            name="pointOfContactPersonName"
                            value={formData.pointOfContactPersonName || ''}
                            onChange={e =>
                                handleChange(
                                    'pointOfContactPersonName',
                                    e.target.value,
                                )
                            }
                            onBlur={() =>
                                handleBlur('pointOfContactPersonName')
                            }
                            variant="outlined"
                            error={
                                touched.pointOfContactPersonName &&
                                Boolean(errors.pointOfContactPersonName)
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
                    )}
                    {isPublic &&
                        touched.pointOfContactPersonName &&
                        errors.pointOfContactPersonName && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={errors.pointOfContactPersonName}
                                />
                            </div>
                        )}
                </div>
                <div className={classes.fieldContainer}>
                    {isPublic && (
                        <DialogTooltip
                            text={
                                "We're making a Premium package for connecting with customers and growing your business. Beta fields preview part of this package and currently appear on your profile. Once the new package is live, you'll get details on keeping those fields active."
                            }
                            childComponent={
                                <span className={classes.betaBadge}>BETA</span>
                            }
                        />
                    )}

                    {isPublic && (
                        <FormFieldTitle
                            label="Contact Email"
                            classes={{ title: classes.formLabel }}
                            required
                        />
                    )}
                    {isPublic && (
                        <TextField
                            fullWidth
                            type="email"
                            name="pointOfContactEmail"
                            value={formData.pointOfContactEmail || ''}
                            onChange={e =>
                                handleChange(
                                    'pointOfContactEmail',
                                    e.target.value,
                                )
                            }
                            onBlur={() => handleBlur('pointOfContactEmail')}
                            variant="outlined"
                            InputProps={{
                                classes: {
                                    input: classes.inputStyles,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            error={
                                touched.pointOfContactEmail &&
                                Boolean(errors.pointOfContactEmail)
                            }
                            placeholder="contact@company.com"
                        />
                    )}
                    {isPublic &&
                        touched.pointOfContactEmail &&
                        errors.pointOfContactEmail && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={errors?.pointOfContactEmail}
                                />
                            </div>
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
    formData: shape({
        yourName: string,
        yourTitle: string,
        pointOfContactPubliclyVisible: bool,
        pointOfContactPersonName: string,
        pointOfContactEmail: string,
        claimantEmploymentVerificationMethod: string,
        claimantLinkedinProfileUrl: string,
        yourBusinessWebsite: string,
        employmentVerificationDocuments: array,
    }).isRequired,
    handleChange: func.isRequired,
    handleBlur: func.isRequired,
    updateFieldWithoutTouch: func.isRequired,
    errors: shape({
        yourName: oneOfType([string, object]),
        yourTitle: oneOfType([string, object]),
        pointOfContactEmail: oneOfType([string, object]),
        pointOfContactPersonName: oneOfType([string, object]),
        claimantEmploymentVerificationMethod: oneOfType([string, object]),
        claimantLinkedinProfileUrl: oneOfType([string, object]),
        yourBusinessWebsite: oneOfType([string, object]),
    }),
    touched: shape({
        yourName: bool,
        yourTitle: bool,
        pointOfContactEmail: bool,
        pointOfContactPersonName: bool,
        claimantEmploymentVerificationMethod: bool,
        claimantLinkedinProfileUrl: bool,
        yourBusinessWebsite: bool,
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
