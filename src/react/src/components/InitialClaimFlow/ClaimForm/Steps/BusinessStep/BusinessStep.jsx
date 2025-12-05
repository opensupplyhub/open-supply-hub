import React, { useState, useEffect } from 'react';
import { func, object } from 'prop-types';
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
import { facilityDetailsRoute } from '../../../../../util/constants';
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
                    name="companyName"
                    value={locationName}
                    InputProps={{
                        className: classes.disabledField,
                        disabled: true,
                        classes: {
                            notchedOutline: classes.notchedOutlineStyles,
                        },
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
                    name="companyAddress"
                    value={locationAddress}
                    InputProps={{
                        className: classes.disabledField,
                        disabled: true,
                        classes: {
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                    }}
                />
            </div>
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
                        <ImportantNote text="We do NOT require and you should NOT submit documents containing sensitive personal information such as salary information, personal phone numbers, home addresses, or personal ID numbers." />
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
                            <ImportantNote text="Verification documents must show the same name and address as listed on Open Supply Hub." />
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
