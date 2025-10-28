import React, { useState, useEffect } from 'react';
import { func, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
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
import useVerificationMethodChange from './hooks';
import { getSelectStyles } from '../../../../../util/util';
import findSelectedOption from '../utils';

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

    // Update previous verification method when it changes.
    useEffect(() => {
        if (formData.companyAddressVerification !== prevVerificationMethod) {
            setPrevVerificationMethod(formData.companyAddressVerification);
        }
    }, [formData.companyAddressVerification]);

    // Clear verification URL when verification method changes.
    useVerificationMethodChange(
        formData.companyAddressVerification,
        prevVerificationMethod,
        handleChange,
    );

    const selectedVerificationMethod = findSelectedOption(
        COMPANY_ADDRESS_VERIFICATION_OPTIONS,
        formData.companyAddressVerification,
    );

    const showUrlInput = requiresUrlInput(selectedVerificationMethod?.value);
    const showDocumentUpload = requiresDocumentUpload(
        selectedVerificationMethod?.value,
    );

    const osId = productionLocationData?.os_id || '';
    const locationName = productionLocationData?.name || '';
    const locationAddress = productionLocationData?.address || '';
    const productionLocationUrl = buildProductionLocationUrl(osId);

    // This checks if the company address verification field has been touched and either has validation errors
    // or no value selected.
    const isCompanyAddressVerificationError = !!(
        touched?.companyAddressVerification &&
        errors?.companyAddressVerification
    );

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <Card className={classes.card}>
                    <CardContent className={classes.content}>
                        <Grid item xs={12} className={classes.section}>
                            <Typography
                                variant="subheading"
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
                        </Grid>
                        <Grid
                            item
                            xs={12}
                            className={classes.verificationSection}
                        >
                            <Typography
                                variant="subheading"
                                className={classes.sectionTitle}
                            >
                                Company Address Verification{' '}
                                <RequiredAsterisk />
                            </Typography>

                            <Typography variant="caption" color="textSecondary">
                                You need to select and provide one of the below
                                items for company address verification.
                            </Typography>

                            <Grid item xs={12} className={classes.selectStyles}>
                                <StyledSelect
                                    id="companyAddressVerification"
                                    name="companyAddressVerification"
                                    aria-label="Company Address Verification"
                                    options={
                                        COMPANY_ADDRESS_VERIFICATION_OPTIONS
                                    }
                                    value={selectedVerificationMethod}
                                    onChange={valueObject => {
                                        handleChange(
                                            'companyAddressVerification',
                                            valueObject.label,
                                        );
                                    }}
                                    onBlur={() =>
                                        handleBlur('companyAddressVerification')
                                    }
                                    styles={getSelectStyles(
                                        isCompanyAddressVerificationError,
                                    )}
                                    placeholder="Choose ONE"
                                    isMulti={false}
                                />
                                {isCompanyAddressVerificationError && (
                                    <Typography className={classes.errorText}>
                                        {errors.companyAddressVerification}
                                    </Typography>
                                )}
                            </Grid>
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
                            {showDocumentUpload && (
                                <Grid
                                    item
                                    xs={12}
                                    className={classes.uploaderContainer}
                                >
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
                                </Grid>
                            )}
                        </Grid>
                        <Grid
                            container
                            className={classes.importantNotice}
                            wrap="nowrap"
                        >
                            <Grid item>
                                <Warning className={classes.noticeIcon} />
                            </Grid>
                            <Grid item xs>
                                <Typography className={classes.noticeText}>
                                    <strong>IMPORTANT!</strong> Verification
                                    documents must show the same name and
                                    address as listed on Open Supply Hub.
                                </Typography>
                            </Grid>
                        </Grid>
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
