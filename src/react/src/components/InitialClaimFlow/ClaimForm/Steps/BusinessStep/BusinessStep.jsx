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
    getVerificationUrlField,
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
        formData.locationAddressVerificationMethod || '',
    );

    // Update previous verification method when it changes.
    useEffect(() => {
        if (
            formData.locationAddressVerificationMethod !==
            prevVerificationMethod
        ) {
            setPrevVerificationMethod(
                formData.locationAddressVerificationMethod,
            );
        }
    }, [formData.locationAddressVerificationMethod]);

    // Clear verification URL and documents when verification method changes.
    useVerificationMethodChange(
        formData.locationAddressVerificationMethod,
        prevVerificationMethod,
        updateFieldWithoutTouch,
    );

    const selectedVerificationMethod = findSelectedOption(
        COMPANY_ADDRESS_VERIFICATION_OPTIONS,
        formData.locationAddressVerificationMethod,
    );

    const showUrlInput = requiresUrlInput(selectedVerificationMethod?.value);
    const showDocumentUpload = requiresDocumentUpload(
        selectedVerificationMethod?.value,
    );

    const osId = productionLocationData?.os_id || '';
    const locationName = productionLocationData?.name || '';
    const locationAddress = productionLocationData?.address || '';
    const productionLocationUrl = facilityDetailsRoute.replace(':osID', osId);

    const isCompanyAddressVerificationError = !!(
        touched.locationAddressVerificationMethod &&
        errors.locationAddressVerificationMethod
    );
    const isCompanyAddressVerificationUrlError = !!(
        touched[getVerificationUrlField(selectedVerificationMethod?.value)] &&
        errors[getVerificationUrlField(selectedVerificationMethod?.value)]
    );
    const isCompanyAddressVerificationDocumentsError = !!(
        touched.companyAddressVerificationDocuments &&
        errors.companyAddressVerificationDocuments
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
                                className={`${classes.sectionTitle} ${classes.verificationSectionTitle}`}
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
                                    id="locationAddressVerificationMethod"
                                    name="locationAddressVerificationMethod"
                                    aria-label="Company Address Verification"
                                    options={
                                        COMPANY_ADDRESS_VERIFICATION_OPTIONS
                                    }
                                    value={selectedVerificationMethod}
                                    onChange={valueObject => {
                                        handleChange(
                                            'locationAddressVerificationMethod',
                                            valueObject.label,
                                        );
                                    }}
                                    onBlur={() =>
                                        handleBlur(
                                            'locationAddressVerificationMethod',
                                        )
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
                                                errors.locationAddressVerificationMethod
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
                                                selectedVerificationMethod?.value,
                                            )}{' '}
                                            <RequiredAsterisk />
                                        </Typography>
                                        <TextField
                                            fullWidth
                                            required
                                            variant="outlined"
                                            name={getVerificationUrlField(
                                                selectedVerificationMethod?.value,
                                            )}
                                            value={
                                                formData[
                                                    getVerificationUrlField(
                                                        selectedVerificationMethod?.value,
                                                    )
                                                ]
                                            }
                                            onChange={e =>
                                                handleChange(
                                                    getVerificationUrlField(
                                                        selectedVerificationMethod?.value,
                                                    ),
                                                    e.target.value,
                                                )
                                            }
                                            onBlur={() =>
                                                handleBlur(
                                                    getVerificationUrlField(
                                                        selectedVerificationMethod?.value,
                                                    ),
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
                                                selectedVerificationMethod?.value,
                                            )}
                                            error={
                                                isCompanyAddressVerificationUrlError
                                            }
                                            helperText={
                                                isCompanyAddressVerificationUrlError && (
                                                    <InputErrorText
                                                        text={
                                                            errors[
                                                                getVerificationUrlField(
                                                                    selectedVerificationMethod?.value,
                                                                )
                                                            ]
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
                                    {isCompanyAddressVerificationDocumentsError && (
                                        <div
                                            className={classes.errorWrapStyles}
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
