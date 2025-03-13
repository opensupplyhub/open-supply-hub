import React from 'react';
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

import ClaimAttachmentsUploader from './ClaimAttachmentsUploader';

import {
    updateClaimAFacilityYourName,
    updateClaimAFacilityYourTitle,
    updateClaimAFacilityYourBusinessWebsite,
    updateClaimAFacilityBusinessWebsite,
    updateClaimAFacilityBusinessLinkedinProfile,
    updateClaimAFacilityUploadFiles,
    updateClaimAFacilityBusinessUploadFiles,
} from '../actions/claimFacility.js';

import { getValueFromEvent } from '../util/util';

import { claimFacilityCommonStyles } from '../util/styles';

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
    uploadFiles,
    businessUploadFiles,
    updateUploadFiles,
    updateBusinessUploadFiles,
    fetching,
    classes,
}) => (
    <>
        <div className={classes.inputGroupStyles}>
            <Typography variant="title" className={classes.titleStyle}>
                Your Contact Information
                <RequiredAsterisk />
            </Typography>
            <Typography variant="subheading" className={classes.boldFontStyle}>
                To confirm your affiliation with this production location, your
                name and job title are required in addition to one of the
                following: business website showing your name and title,
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
            <Typography variant="title" className={classes.titleStyle}>
                Business Contact Information
                <RequiredAsterisk />
            </Typography>
            <Typography variant="subheading" className={classes.boldFontStyle}>
                To confirm the name and address of the production location, at
                least one of the following documents is required: utility bill,
                business website, registration document, or LinkedIn profile.
            </Typography>
            <Typography variant="subheading" className={classes.boldFontStyle}>
                Please make sure to provide enough documentation to confirm the
                production location’s name AND address.
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

ClaimFacilitySupportDocs.defaultProps = {
    uploadFiles: [],
    businessUploadFiles: [],
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
                uploadFiles,
                businessUploadFiles,
            },
            fetching,
        },
    },
}) => ({
    yourName,
    yourTitle,
    yourBusinessWebsite,
    businessWebsite,
    businessLinkedinProfile,
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
    updateUploadFiles: files =>
        dispatch(updateClaimAFacilityUploadFiles(files)),
    updateBusinessUploadFiles: files =>
        dispatch(updateClaimAFacilityBusinessUploadFiles(files)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimFacilityCommonStyles)(ClaimFacilitySupportDocs));
