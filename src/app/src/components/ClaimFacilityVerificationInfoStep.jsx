import React from 'react';
import { bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import isEmpty from 'lodash/isEmpty';
import { isURL } from 'validator';
import ClaimAttachmentsUploader from './ClaimAttachmentsUploader';

import {
    updateClaimAFacilityVerificationMethod,
    updateClaimAFacilityLinkedinProfile,
} from '../actions/claimFacility';

import { getValueFromEvent } from '../util/util';

import { claimAFacilityFormStyles } from '../util/styles';

import { claimAFacilityFormFields } from '../util/constants';

const {
    verificationMethod: verificationMethodFormField,
    facilityLinkedinProfile: facilityLinkedinProfileFormField,
    claimAdditionalDocumentation: claimAdditionalDocumentationFormField,
} = claimAFacilityFormFields;

function ClaimFacilityVerificationInfoStep({
    verificationMethod,
    updateVerification,
    fetching,
    facilityLinkedinProfile,
    updateLinkedinProfile,
}) {
    return (
        <>
            <div style={claimAFacilityFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={facilityLinkedinProfileFormField.id}>
                    <Typography variant="title">
                        {facilityLinkedinProfileFormField.label}
                    </Typography>
                </InputLabel>
                <TextField
                    id={facilityLinkedinProfileFormField.id}
                    error={
                        !isEmpty(facilityLinkedinProfile) &&
                        !isURL(facilityLinkedinProfile)
                    }
                    variant="outlined"
                    style={claimAFacilityFormStyles.textFieldStyles}
                    value={facilityLinkedinProfile}
                    onChange={updateLinkedinProfile}
                    disabled={fetching}
                />
            </div>
            <div style={claimAFacilityFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={verificationMethodFormField.id}>
                    <Typography variant="title">
                        {verificationMethodFormField.label}
                    </Typography>
                </InputLabel>
                <TextField
                    id={verificationMethodFormField.id}
                    variant="outlined"
                    multiline
                    rows={4}
                    style={claimAFacilityFormStyles.textFieldStyles}
                    value={verificationMethod}
                    onChange={updateVerification}
                    disabled={fetching}
                />
                <Typography style={{ marginRight: '20px' }}>
                    If you do not have a website or LinkedIn page for your
                    facility, or if those pages do not list the address of the
                    facility you wish to claim, please email{' '}
                    <a href="mailto:data@opensupplyhub.org">
                        data@opensupplyhub.org
                    </a>{' '}
                    with documentation confirming the address of your facility,
                    to assist the OS Hub team in verifying your claim.
                </Typography>
            </div>
            <div style={claimAFacilityFormStyles.inputGroupStyles}>
                <Typography variant="title">
                    {claimAdditionalDocumentationFormField.label}
                </Typography>
                <ClaimAttachmentsUploader />
            </div>
        </>
    );
}

ClaimFacilityVerificationInfoStep.propTypes = {
    verificationMethod: string.isRequired,
    fetching: bool.isRequired,
    updateVerification: func.isRequired,
    facilityLinkedinProfile: string.isRequired,
    updateLinkedinProfile: func.isRequired,
};

function mapStateToProps({
    claimFacility: {
        claimData: {
            formData: { verificationMethod, facilityLinkedinProfile },
            fetching,
        },
    },
}) {
    return {
        verificationMethod,
        fetching,
        facilityLinkedinProfile,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateVerification: e =>
            dispatch(
                updateClaimAFacilityVerificationMethod(getValueFromEvent(e)),
            ),
        updateLinkedinProfile: e =>
            dispatch(updateClaimAFacilityLinkedinProfile(getValueFromEvent(e))),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimFacilityVerificationInfoStep);
