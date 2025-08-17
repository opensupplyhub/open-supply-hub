import React, { useEffect } from 'react';
import { bool, func, string, PropTypes, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import isEmpty from 'lodash/isEmpty';
import every from 'lodash/every';
import { isURL } from 'validator';

import RequiredAsterisk from './RequiredAsterisk';
import InputSection from './InputSection';

import ClaimAttachmentsUploader from './ClaimAttachmentsUploader';

import {
    updateClaimAFacilityYourName,
    updateClaimAFacilityYourTitle,
    updateClaimAFacilityYourBusinessWebsite,
    updateClaimAFacilityBusinessWebsite,
    updateClaimAFacilityBusinessLinkedinProfile,
    updateClaimAFacilityClaimReason,
    updateClaimAFacilityClaimReasonOther,
    fetchClaimsReasons,
    updateClaimAFacilityUploadFiles,
    updateClaimAFacilityBusinessUploadFiles,
} from '../actions/claimFacility.js';

import { getValueFromEvent } from '../util/util';

import { claimedFacilitiesDetailsStyles } from '../util/styles';

import { claimAFacilitySupportDocsFormFields } from '../util/constants';

const {
    contactYourName,
    contactYourTitle,
    contactYourBusinessWebsite,
    yourAdditionalDocumentationTitle,
    businessAdditionalDocumentationTitle,
    additionalDocumentationSub,
    contactBusinessWebsite,
    contactBusinessLinkedinProfile,
} = claimAFacilitySupportDocsFormFields;

const ClaimFacilitySupportDocs = ({
    yourName,
    updateYourName,
    yourTitle,
    updateYourTitle,
    yourBusinessWebsite,
    updateYourBusinessWebsite,
    businessWebsite,
    updateBusinessWebsite,
    businessLinkedinProfile,
    updateBusinessLinkedinProfile,
    claimReason,
    updateClaimReason,
    claimReasonOther,
    updateClaimReasonOther,
    claimsReasons,
    fetchClaimsReasonsData,
    uploadFiles,
    businessUploadFiles,
    updateUploadFiles,
    updateBusinessUploadFiles,
    fetching,
    classes,
}) => {
    useEffect(() => {
        if (!claimsReasons) {
            fetchClaimsReasonsData();
        }
    }, [claimsReasons, fetchClaimsReasonsData]);

    const claimsReasonOptions = claimsReasons
        ? [
              ...claimsReasons.map(reason => ({
                  value: reason.text,
                  label: reason.text,
              })),
              { value: 'Other', label: 'Other' },
          ]
        : [{ value: 'Other', label: 'Other' }];

    const showOtherField = claimReason === 'Other';
    const remainingChars =
        100 - (claimReasonOther ? claimReasonOther.length : 0);

    return (
        <>
            <div className={classes.inputGroupStyles}>
                <Typography variant="title" className={classes.boldTitleStyle}>
                    Your Contact Information
                    <RequiredAsterisk />
                </Typography>
                <Typography
                    variant="subheading"
                    className={classes.boldFontStyle}
                >
                    To confirm your affiliation with this production location,
                    your name and job title are required in addition to one of
                    the following: business website showing your name and title,
                    employment badge, letter of employment, or other relevant
                    employment documentation.
                </Typography>
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={contactYourName.id}>
                    <Typography variant="title">
                        {contactYourName.label}
                        <RequiredAsterisk />
                    </Typography>
                </InputLabel>
                <TextField
                    autoFocus
                    error={isEmpty(yourName)}
                    id={contactYourName.id}
                    variant="outlined"
                    className={classes.textFieldStyles}
                    value={yourName}
                    placeholder={contactYourName.placeholder}
                    onChange={updateYourName}
                    disabled={fetching}
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={contactYourTitle.id}>
                    <Typography variant="title">
                        {contactYourTitle.label}
                        <RequiredAsterisk />
                    </Typography>
                </InputLabel>
                <TextField
                    error={isEmpty(yourTitle)}
                    id={contactYourTitle.id}
                    variant="outlined"
                    className={classes.textFieldStyles}
                    value={yourTitle}
                    placeholder={contactYourTitle.placeholder}
                    onChange={updateYourTitle}
                    disabled={fetching}
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={contactYourBusinessWebsite.id}>
                    <Typography variant="title">
                        {contactYourBusinessWebsite.label}
                    </Typography>
                </InputLabel>
                <TextField
                    id={contactYourBusinessWebsite.id}
                    error={every([
                        !isEmpty(yourBusinessWebsite),
                        !isURL(yourBusinessWebsite),
                    ])}
                    variant="outlined"
                    className={classes.textFieldStyles}
                    value={yourBusinessWebsite}
                    placeholder={contactYourBusinessWebsite.placeholder}
                    onChange={updateYourBusinessWebsite}
                    disabled={fetching}
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <Typography variant="title">
                    {yourAdditionalDocumentationTitle.label}
                </Typography>
                <Typography variant="subheading">
                    {additionalDocumentationSub.label}
                </Typography>
                <ClaimAttachmentsUploader
                    inputId="yourFiles"
                    title="Upload an employment badge, letter of employment, or
                other relevant employment documentation to confirm your name and title."
                    files={uploadFiles}
                    updateUploadFiles={updateUploadFiles}
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <Typography variant="title" className={classes.boldTitleStyle}>
                    Business Contact Information
                    <RequiredAsterisk />
                </Typography>
                <Typography
                    variant="subheading"
                    className={classes.boldFontStyle}
                >
                    To confirm the name and address of the production location,
                    at least one of the following documents is required: utility
                    bill, business website, registration document, or LinkedIn
                    profile.
                </Typography>
                <Typography
                    variant="subheading"
                    className={classes.boldFontStyle}
                >
                    Please make sure to provide enough documentation to confirm
                    the production location’s name AND address.
                </Typography>
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={contactBusinessWebsite.id}>
                    <Typography variant="title">
                        {contactBusinessWebsite.label}
                    </Typography>
                </InputLabel>
                <TextField
                    id={contactBusinessWebsite.id}
                    error={every([
                        !isEmpty(businessWebsite),
                        !isURL(businessWebsite),
                    ])}
                    variant="outlined"
                    className={classes.textFieldStyles}
                    value={businessWebsite}
                    placeholder={contactBusinessWebsite.placeholder}
                    onChange={updateBusinessWebsite}
                    disabled={fetching}
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={contactBusinessLinkedinProfile.id}>
                    <Typography variant="title">
                        {contactBusinessLinkedinProfile.label}
                    </Typography>
                </InputLabel>
                <TextField
                    id={contactBusinessLinkedinProfile.id}
                    error={every([
                        !isEmpty(businessLinkedinProfile),
                        !isURL(businessLinkedinProfile),
                    ])}
                    variant="outlined"
                    className={classes.textFieldStyles}
                    value={businessLinkedinProfile}
                    placeholder={contactBusinessLinkedinProfile.placeholder}
                    onChange={updateBusinessLinkedinProfile}
                    disabled={fetching}
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel>
                    <Typography
                        variant="title"
                        className={classes.boldTitleStyle}
                    >
                        What made you decide to claim?
                    </Typography>
                </InputLabel>
                <InputSection
                    value={claimReason}
                    onChange={updateClaimReason}
                    disabled={fetching}
                    isSelect
                    selectOptions={claimsReasonOptions}
                    selectPlaceholder="Select a reason"
                />
                {showOtherField && (
                    <div style={{ marginTop: '16px' }}>
                        <TextField
                            variant="outlined"
                            className={classes.textFieldStyles}
                            value={claimReasonOther}
                            placeholder="Please specify"
                            onChange={updateClaimReasonOther}
                            disabled={fetching}
                            inputProps={{ maxLength: 100 }}
                            helperText={`${remainingChars}/100 characters remaining`}
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                        />
                    </div>
                )}
            </div>
            <div className={classes.inputGroupStyles}>
                <Typography variant="title">
                    {businessAdditionalDocumentationTitle.label}
                </Typography>
                <Typography variant="subheading">
                    {additionalDocumentationSub.label}
                </Typography>
                <ClaimAttachmentsUploader
                    inputId="businessFiles"
                    title="Upload a utility bill, business registration document or
                other relevant documentation to confirm the production location’s name and address."
                    files={businessUploadFiles}
                    updateUploadFiles={updateBusinessUploadFiles}
                />
            </div>
        </>
    );
};

ClaimFacilitySupportDocs.defaultProps = {
    uploadFiles: [],
    businessUploadFiles: [],
    claimsReasons: null,
};

ClaimFacilitySupportDocs.propTypes = {
    yourName: string.isRequired,
    updateYourName: func.isRequired,
    yourTitle: string.isRequired,
    updateYourTitle: func.isRequired,
    yourBusinessWebsite: string.isRequired,
    updateYourBusinessWebsite: func.isRequired,
    businessWebsite: string.isRequired,
    updateBusinessWebsite: func.isRequired,
    businessLinkedinProfile: string.isRequired,
    updateBusinessLinkedinProfile: func.isRequired,
    claimReason: string.isRequired,
    updateClaimReason: func.isRequired,
    claimReasonOther: string.isRequired,
    updateClaimReasonOther: func.isRequired,
    claimsReasons: PropTypes.arrayOf(PropTypes.object),
    fetchClaimsReasonsData: func.isRequired,
    uploadFiles: PropTypes.arrayOf(PropTypes.object),
    businessUploadFiles: PropTypes.arrayOf(PropTypes.object),
    updateUploadFiles: PropTypes.func.isRequired,
    updateBusinessUploadFiles: PropTypes.func.isRequired,
    fetching: bool.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    claimFacility: {
        claimData: {
            formData: {
                yourName,
                yourTitle,
                yourBusinessWebsite,
                businessWebsite,
                businessLinkedinProfile,
                claimReason,
                claimReasonOther,
                uploadFiles,
                businessUploadFiles,
            },
            fetching,
        },
        claimsReasons: { data: claimsReasons },
    },
}) => ({
    yourName,
    yourTitle,
    yourBusinessWebsite,
    businessWebsite,
    businessLinkedinProfile,
    claimReason,
    claimReasonOther,
    claimsReasons,
    uploadFiles,
    businessUploadFiles,
    fetching,
});

const mapDispatchToProps = dispatch => ({
    updateYourName: e =>
        dispatch(updateClaimAFacilityYourName(getValueFromEvent(e))),
    updateYourTitle: e =>
        dispatch(updateClaimAFacilityYourTitle(getValueFromEvent(e))),
    updateYourBusinessWebsite: e =>
        dispatch(updateClaimAFacilityYourBusinessWebsite(getValueFromEvent(e))),
    updateBusinessWebsite: e =>
        dispatch(updateClaimAFacilityBusinessWebsite(getValueFromEvent(e))),
    updateBusinessLinkedinProfile: e =>
        dispatch(
            updateClaimAFacilityBusinessLinkedinProfile(getValueFromEvent(e)),
        ),
    updateClaimReason: selection =>
        dispatch(
            updateClaimAFacilityClaimReason(selection ? selection.value : ''),
        ),
    updateClaimReasonOther: e =>
        dispatch(updateClaimAFacilityClaimReasonOther(getValueFromEvent(e))),
    fetchClaimsReasonsData: () => dispatch(fetchClaimsReasons()),
    updateUploadFiles: files =>
        dispatch(updateClaimAFacilityUploadFiles(files)),
    updateBusinessUploadFiles: files =>
        dispatch(updateClaimAFacilityBusinessUploadFiles(files)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimedFacilitiesDetailsStyles)(ClaimFacilitySupportDocs));
