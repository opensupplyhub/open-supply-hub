import React, { useState, useEffect } from 'react';
import { func, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import Language from '@material-ui/icons/Language';
import Warning from '@material-ui/icons/Warning';

import RequiredAsterisk from '../../../../RequiredAsterisk';
import StyledSelect from '../../../../Filters/StyledSelect';
import ClaimAttachmentsUploader from '../../../../ClaimAttachmentsUploader';
import withScrollReset from '../../../HOCs/withScrollReset';

import businessStepStyles from './styles';
import { COMPANY_ADDRESS_VERIFICATION_OPTIONS } from './constants';
import {
    requiresUrlInput,
    requiresDocumentUpload,
    getUrlPlaceholder,
    getUrlLabel,
    buildProductionLocationUrl,
} from './utils';
import { useVerificationMethodChange } from './hooks';
import { getSelectStyles } from '../../../../../util/util';

const BusinessStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    errors,
    touched,
    productionLocationData,
}) => {
    const [prevVerificationMethod, setPrevVerificationMethod] = useState(
        formData.companyAddressVerification || '',
    );

    // Update previous verification method when it changes
    useEffect(() => {
        if (formData.companyAddressVerification !== prevVerificationMethod) {
            setPrevVerificationMethod(formData.companyAddressVerification);
        }
    }, [formData.companyAddressVerification]);

    // Clear verification URL when verification method changes
    useVerificationMethodChange(
        formData.companyAddressVerification,
        prevVerificationMethod,
        handleChange,
    );

    const showUrlInput = requiresUrlInput(formData.companyAddressVerification);
    const showDocumentUpload = requiresDocumentUpload(
        formData.companyAddressVerification,
    );

    const osId = productionLocationData?.os_id || '';
    const locationName = productionLocationData?.name || '';
    const locationAddress = productionLocationData?.address || '';
    const productionLocationUrl = buildProductionLocationUrl(osId);

    // Convert verification options to format expected by StyledSelect
    const verificationOptions = COMPANY_ADDRESS_VERIFICATION_OPTIONS.map(
        option => ({
            value: option.value,
            label: option.label,
        }),
    );

    // Convert selected verification method to format expected by StyledSelect
    const selectedVerificationMethod = formData.companyAddressVerification
        ? verificationOptions.find(
              opt => opt.value === formData.companyAddressVerification,
          )
        : null;

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <Card className={classes.card}>
                    <CardHeader
                        className={classes.cardHeader}
                        title={
                            <Typography variant="title">
                                <Language className={classes.headerIcon} />
                                Business Information
                            </Typography>
                        }
                    />
                    <CardContent className={classes.content}>
                        <Typography variant="body1" className={classes.section}>
                            Verify the company address for this production
                            location
                        </Typography>

                        {/* Production Location Details */}
                        <div className={classes.section}>
                            <Typography
                                variant="subtitle1"
                                className={classes.sectionTitle}
                            >
                                Production Location Details
                            </Typography>

                            <Grid container spacing={16}>
                                <Grid item xs={12}>
                                    <Typography
                                        variant="caption"
                                        color="textSecondary"
                                    >
                                        OS ID
                                    </Typography>
                                    <a
                                        href={productionLocationUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className={classes.linkField}
                                    >
                                        {osId}
                                    </a>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        disabled
                                        name="companyName"
                                        label="Company Name"
                                        value={locationName}
                                        className={classes.field}
                                        InputProps={{
                                            className: classes.disabledField,
                                        }}
                                    />
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        disabled
                                        multiline
                                        rows={2}
                                        name="companyAddress"
                                        label="Company Address"
                                        value={locationAddress}
                                        className={classes.field}
                                        InputProps={{
                                            className: classes.disabledField,
                                        }}
                                    />
                                </Grid>
                            </Grid>
                        </div>

                        {/* Company Address Verification */}
                        <div className={classes.verificationSection}>
                            <Typography
                                variant="subtitle1"
                                className={classes.sectionTitle}
                            >
                                Company Address Verification{' '}
                                <RequiredAsterisk />
                            </Typography>

                            <Typography variant="caption" color="textSecondary">
                                You need to select and provide one of the below
                                items for company address verification.
                            </Typography>

                            <div className={classes.selectStyles}>
                                <StyledSelect
                                    id="companyAddressVerification"
                                    name="companyAddressVerification"
                                    aria-label="Company Address Verification"
                                    options={verificationOptions}
                                    value={selectedVerificationMethod}
                                    onChange={value => {
                                        handleChange(
                                            'companyAddressVerification',
                                            value ? value.value : '',
                                        );
                                    }}
                                    onBlur={e => {
                                        const event = {
                                            ...e,
                                            target: {
                                                ...e.target,
                                                name:
                                                    'companyAddressVerification',
                                            },
                                        };
                                        handleBlur(event);
                                    }}
                                    styles={getSelectStyles(
                                        touched.companyAddressVerification &&
                                            !!errors.companyAddressVerification,
                                    )}
                                    placeholder="Choose ONE"
                                    isMulti={false}
                                />
                                {touched.companyAddressVerification &&
                                    errors.companyAddressVerification && (
                                        <Typography
                                            className={classes.errorText}
                                        >
                                            {errors.companyAddressVerification}
                                        </Typography>
                                    )}
                            </div>

                            {/* URL Input for website/LinkedIn verification */}
                            {showUrlInput && (
                                <Grid container spacing={16}>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            required
                                            name="verificationUrl"
                                            label={getUrlLabel(
                                                formData.companyAddressVerification,
                                            )}
                                            value={
                                                formData.verificationUrl || ''
                                            }
                                            onChange={e =>
                                                handleChange(
                                                    'verificationUrl',
                                                    e.target.value,
                                                )
                                            }
                                            onBlur={handleBlur}
                                            className={classes.field}
                                            placeholder={getUrlPlaceholder(
                                                formData.companyAddressVerification,
                                            )}
                                            error={
                                                touched.verificationUrl &&
                                                !!errors.verificationUrl
                                            }
                                            helperText={
                                                touched.verificationUrl &&
                                                errors.verificationUrl
                                            }
                                            FormHelperTextProps={{
                                                className: classes.helperText,
                                            }}
                                        />
                                    </Grid>
                                </Grid>
                            )}

                            {/* Document Upload for document-based verification */}
                            {showDocumentUpload && (
                                <div className={classes.uploaderContainer}>
                                    <ClaimAttachmentsUploader
                                        inputId="company-address-verification-documents"
                                        title="Upload your documents"
                                        files={
                                            formData.verificationDocuments || []
                                        }
                                        updateUploadFiles={files =>
                                            handleChange(
                                                'verificationDocuments',
                                                files,
                                            )
                                        }
                                    />
                                </div>
                            )}
                        </div>

                        {/* Important Notice */}
                        <div className={classes.importantNotice}>
                            <Warning className={classes.noticeIcon} />
                            <div>
                                <Typography className={classes.noticeText}>
                                    <strong>IMPORTANT!</strong> Verification
                                    documents must show the same name and
                                    address as listed on Open Supply Hub.
                                </Typography>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
};

BusinessStep.defaultProps = {
    errors: {},
    touched: {},
    productionLocationData: {},
};

BusinessStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    handleBlur: func.isRequired,
    errors: object,
    touched: object,
    productionLocationData: object,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        singleProductionLocation: { data: productionLocationData },
    },
}) => ({
    productionLocationData,
});

export default connect(mapStateToProps)(
    withStyles(businessStepStyles)(withScrollReset(BusinessStep)),
);
