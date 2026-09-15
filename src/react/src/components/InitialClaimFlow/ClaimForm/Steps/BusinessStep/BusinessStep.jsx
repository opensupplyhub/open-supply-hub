import React, { useState, useEffect } from 'react';
import { bool, func, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import { Link } from 'react-router-dom';

import FormFieldTitle from '../../../Shared/FormFieldTitle/FormFieldTitle';
import ImportantNote from '../../../Shared/ImportantNote/ImportantNote';
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
import {
    facilityDetailsRoute,
    contributeProductionLocationRoute,
    ENABLE_CLAIM_NAME_ADDRESS_EDIT,
    CLAIM_PII_WARNING_TEXT,
} from '../../../../../util/constants';
import { selectStyles } from '../../styles';

const BusinessStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    errors,
    touched,
    productionLocationData,
    updateFieldWithoutTouch,
    isNameAddressEditable,
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
    const isCompanyNameError = !!(
        touched.facilityNameEnglish && errors.facilityNameEnglish
    );
    const isCompanyAddressError = !!(
        touched.facilityAddress && errors.facilityAddress
    );

    // While the switch is off the fields are read-only copies of the
    // production location's values. While it is on they are bound to the
    // form so the claimant's edits are submitted with the claim.
    const companyNameValue = isNameAddressEditable
        ? formData.facilityNameEnglish ?? ''
        : locationName;
    const companyAddressValue = isNameAddressEditable
        ? formData.facilityAddress ?? ''
        : locationAddress;

    // The aria-label lives inside InputProps.inputProps because the lint
    // rule react/jsx-no-duplicate-props treats `inputProps` and `InputProps`
    // on the same element as duplicates.
    const getCompanyFieldInputProps = ariaLabel => ({
        ...(isNameAddressEditable
            ? {}
            : { className: classes.disabledField, disabled: true }),
        inputProps: { 'aria-label': ariaLabel },
        classes: {
            notchedOutline: classes.notchedOutlineStyles,
        },
    });
    const documentsMatchNoteText = isNameAddressEditable
        ? 'Verification documents must show the same name and address as entered above.'
        : 'Verification documents must show the same name and address as listed on Open Supply Hub.';

    return (
        <div>
            <div className={classes.formFieldContainer}>
                <FormFieldTitle
                    label="OS ID"
                    classes={{ title: classes.formLabelRoot }}
                    required
                />
                <Link
                    to={productionLocationUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={classes.linkField}
                >
                    {osId}
                </Link>
            </div>
            <div className={classes.formFieldContainer}>
                <FormFieldTitle
                    label="Company Name"
                    classes={{ title: classes.formLabel }}
                    required
                />
                <TextField
                    fullWidth
                    variant="outlined"
                    multiline
                    name="facilityNameEnglish"
                    id="facilityNameEnglish"
                    value={companyNameValue}
                    onChange={e =>
                        handleChange('facilityNameEnglish', e.target.value)
                    }
                    onBlur={() => handleBlur('facilityNameEnglish')}
                    InputProps={getCompanyFieldInputProps('Company Name')}
                    error={isCompanyNameError}
                    helperText={
                        isCompanyNameError && (
                            <InputErrorText text={errors.facilityNameEnglish} />
                        )
                    }
                    FormHelperTextProps={{
                        className: classes.helperText,
                    }}
                />
            </div>
            <div className={classes.formFieldContainer}>
                <FormFieldTitle
                    label="Company Address"
                    classes={{ title: classes.formLabel }}
                    required
                />
                <TextField
                    fullWidth
                    variant="outlined"
                    multiline
                    name="facilityAddress"
                    id="facilityAddress"
                    value={companyAddressValue}
                    onChange={e =>
                        handleChange('facilityAddress', e.target.value)
                    }
                    onBlur={() => handleBlur('facilityAddress')}
                    InputProps={getCompanyFieldInputProps('Company Address')}
                    error={isCompanyAddressError}
                    helperText={
                        isCompanyAddressError && (
                            <InputErrorText text={errors.facilityAddress} />
                        )
                    }
                    FormHelperTextProps={{
                        className: classes.helperText,
                    }}
                />
            </div>
            {isNameAddressEditable && (
                <div className={classes.nameAddressNoteWrapper}>
                    <ImportantNote
                        text={
                            <>
                                The name and address you enter here will be
                                shown on the production location page once your
                                claim is approved, and they must match the name
                                and address on the document or web page you
                                submit for verification. If this production
                                location has moved to a new address, do not edit
                                the address here. Instead, submit the new
                                location through the{' '}
                                <Link
                                    to={contributeProductionLocationRoute}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={classes.noteLink}
                                >
                                    Single Location Contribution form
                                </Link>{' '}
                                so a new OS ID can be created.
                            </>
                        }
                    />
                </div>
            )}
            <div className={classes.formFieldContainer}>
                <FormFieldTitle
                    label="Company Address Verification"
                    classes={{ title: classes.formLabel }}
                    required
                />
                <Typography
                    variant="body1"
                    className={classes.sectionDescription}
                >
                    You need to select and provide one of the below items for
                    company address verification.
                </Typography>
                <StyledSelect
                    id="locationAddressVerificationMethod"
                    name="locationAddressVerificationMethod"
                    aria-label="Company Address Verification"
                    options={COMPANY_ADDRESS_VERIFICATION_OPTIONS}
                    value={selectedVerificationMethod}
                    onChange={valueObject => {
                        handleChange(
                            'locationAddressVerificationMethod',
                            valueObject.label,
                        );
                    }}
                    onBlur={() =>
                        handleBlur('locationAddressVerificationMethod')
                    }
                    styles={getSelectStyles(
                        isCompanyAddressVerificationError,
                        selectStyles,
                    )}
                    placeholder="You need to provide one of the below items for address verification"
                    isMulti={false}
                />
                {isCompanyAddressVerificationError && (
                    <div className={classes.errorWrapStyles}>
                        <InputErrorText
                            text={errors.locationAddressVerificationMethod}
                        />
                    </div>
                )}
            </div>
            <div className={classes.documentUploadContainer}>
                {showDocumentUpload && (
                    <Grid item xs={12}>
                        <ImportantNote text={CLAIM_PII_WARNING_TEXT} />
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
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText
                                    text={
                                        errors.companyAddressVerificationDocuments
                                    }
                                />
                            </div>
                        )}
                        <div className={classes.importantNoteWrapper}>
                            <ImportantNote text={documentsMatchNoteText} />
                        </div>
                    </Grid>
                )}
            </div>
            <div className={classes.formFieldContainer}>
                {showUrlInput && (
                    <FormFieldTitle
                        label={getUrlLabel(selectedVerificationMethod?.value)}
                        classes={{ title: classes.formLabel }}
                        required
                    />
                )}
                {showUrlInput && (
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
                                notchedOutline: classes.notchedOutlineStyles,
                            },
                        }}
                        placeholder={getUrlPlaceholder(
                            selectedVerificationMethod?.value,
                        )}
                        error={isCompanyAddressVerificationUrlError}
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
                )}
            </div>
        </div>
    );
};

BusinessStep.defaultProps = {
    errors: {},
    touched: {},
    productionLocationData: {},
    isNameAddressEditable: false,
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
    isNameAddressEditable: bool,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        singleProductionLocation: { data: productionLocationData },
    },
    featureFlags: { flags },
}) => ({
    productionLocationData,
    isNameAddressEditable: !!flags[ENABLE_CLAIM_NAME_ADDRESS_EDIT],
});

export default connect(mapStateToProps)(
    withStyles(businessStepStyles)(withScrollReset(BusinessStep)),
);
