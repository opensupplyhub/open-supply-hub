import React, { useState, useEffect } from 'react';
import { func, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import InfoIcon from '@material-ui/icons/Info';
import { Link } from 'react-router-dom';

import RequiredAsterisk from '../../../../RequiredAsterisk';
import StyledSelect from '../../../../Filters/StyledSelect';
import InputErrorText from '../../../../Contribute/InputErrorText';
import ClaimAttachmentsUploader from '../../../../ClaimAttachmentsUploader';
import withScrollReset from '../../../HOCs/withScrollReset';

import businessStepStyles from './styles';
import { COMPANY_ADDRESS_VERIFICATION_OPTIONS } from './constants';
import {
    requiresUrlInput,
    requiresDocumentUpload,
    getUrlPlaceholder,
    getUrlLabel,
} from './utils';
import useVerificationMethodChange from './hooks';
import { getSelectStyles } from '../../../../../util/util';
import findSelectedOption from '../utils';
import { facilityDetailsRoute } from '../../../../../util/constants';

const BusinessStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    errors,
    touched,
    productionLocationData,
    updateFieldWithoutTouch,
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

    // Clear verification URL and documents when verification method changes.
    useVerificationMethodChange(
        formData.companyAddressVerification,
        prevVerificationMethod,
        updateFieldWithoutTouch,
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
    const productionLocationUrl = facilityDetailsRoute.replace(':osID', osId);

    // This checks if the company address verification field has been touched and either has validation errors
    // or no value selected.
    const isCompanyAddressVerificationError = !!(
        touched?.companyAddressVerification &&
        errors?.companyAddressVerification
    );

    // This checks if the company address verification URL field has been touched and has validation errors.
    const isCompanyAddressVerificationUrlError = !!(
        touched.companyAddressVerificationUrl &&
        errors.companyAddressVerificationUrl
    );

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <Card className={classes.card}>
                    <CardContent className={classes.content}>
                        <Grid
                            item
                            xs={12}
                            className={classes.productionLocationSection}
                        >
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
                                        className={classes.fieldLabel}
                                    >
                                        OS ID
                                    </Typography>
                                    <Link
                                        to={productionLocationUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className={classes.linkField}
                                    >
                                        {osId}
                                    </Link>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Typography
                                        variant="caption"
                                        color="textSecondary"
                                        className={classes.fieldLabel}
                                    >
                                        Company Name
                                    </Typography>
                                    <TextField
                                        fullWidth
                                        disabled
                                        variant="outlined"
                                        multiline
                                        name="companyName"
                                        value={locationName}
                                        InputProps={{
                                            className: classes.disabledField,
                                            classes: {
                                                notchedOutline:
                                                    classes.notchedOutlineStyles,
                                            },
                                        }}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Typography
                                        variant="caption"
                                        color="textSecondary"
                                        className={classes.fieldLabel}
                                    >
                                        Company Address
                                    </Typography>
                                    <TextField
                                        fullWidth
                                        disabled
                                        variant="outlined"
                                        multiline
                                        name="companyAddress"
                                        value={locationAddress}
                                        InputProps={{
                                            className: classes.disabledField,
                                            classes: {
                                                notchedOutline:
                                                    classes.notchedOutlineStyles,
                                            },
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
                                className={`${classes.sectionTitle} ${classes.verficationSectionTitle}`}
                            >
                                Company Address Verification{' '}
                                <RequiredAsterisk />
                            </Typography>
                            <Typography
                                variant="caption"
                                color="textSecondary"
                                className={classes.verificationDescription}
                            >
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
                                    <div className={classes.errorWrapStyles}>
                                        <InputErrorText
                                            text={
                                                errors.companyAddressVerification
                                            }
                                        />
                                    </div>
                                )}
                            </Grid>
                            {showUrlInput && (
                                <Grid container>
                                    <Grid item xs={12}>
                                        <Typography
                                            variant="caption"
                                            color="textSecondary"
                                            className={classes.fieldLabel}
                                        >
                                            {getUrlLabel(
                                                formData.companyAddressVerification,
                                            )}{' '}
                                            <RequiredAsterisk />
                                        </Typography>
                                        <TextField
                                            fullWidth
                                            required
                                            variant="outlined"
                                            name="companyAddressVerificationUrl"
                                            value={
                                                formData.companyAddressVerificationUrl
                                            }
                                            onChange={e =>
                                                handleChange(
                                                    'companyAddressVerificationUrl',
                                                    e.target.value,
                                                )
                                            }
                                            onBlur={() =>
                                                handleBlur(
                                                    'companyAddressVerificationUrl',
                                                )
                                            }
                                            InputProps={{
                                                classes: {
                                                    notchedOutline:
                                                        classes.notchedOutlineStyles,
                                                    input: `
                                                    ${
                                                        isCompanyAddressVerificationUrlError &&
                                                        classes.errorInput
                                                    }`,
                                                },
                                            }}
                                            placeholder={getUrlPlaceholder(
                                                formData.companyAddressVerification,
                                            )}
                                            error={
                                                isCompanyAddressVerificationUrlError
                                            }
                                            helperText={
                                                isCompanyAddressVerificationUrlError && (
                                                    <InputErrorText
                                                        text={
                                                            errors.companyAddressVerificationUrl
                                                        }
                                                    />
                                                )
                                            }
                                            FormHelperTextProps={{
                                                className: classes.helperText,
                                            }}
                                        />
                                    </Grid>
                                </Grid>
                            )}
                            {showDocumentUpload && (
                                <Grid item xs={12}>
                                    <ClaimAttachmentsUploader
                                        inputId="company-address-verification-documents"
                                        title="Upload your documents"
                                        files={
                                            formData.companyAddressVerificationDocuments ||
                                            []
                                        }
                                        updateUploadFiles={files =>
                                            handleChange(
                                                'companyAddressVerificationDocuments',
                                                files,
                                            )
                                        }
                                    />
                                    {touched.companyAddressVerificationDocuments &&
                                        !!errors.companyAddressVerificationDocuments && (
                                            <div
                                                className={
                                                    classes.errorWrapStyles
                                                }
                                            >
                                                <InputErrorText
                                                    text={
                                                        errors.companyAddressVerificationDocuments
                                                    }
                                                />
                                            </div>
                                        )}
                                </Grid>
                            )}
                        </Grid>
                        <Grid
                            container
                            className={classes.warningBox}
                            wrap="nowrap"
                        >
                            <Grid item className={classes.warningIconContainer}>
                                <InfoIcon className={classes.warningIcon} />
                            </Grid>
                            <Grid item xs>
                                <Typography className={classes.warningText}>
                                    <span className={classes.warningBoldText}>
                                        IMPORTANT!
                                    </span>{' '}
                                    Verification documents must show the same
                                    name and address as listed on Open Supply
                                    Hub.
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
    updateFieldWithoutTouch: func.isRequired,
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
