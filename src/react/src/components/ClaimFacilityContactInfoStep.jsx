import React from 'react';
import { bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import isEmpty from 'lodash/isEmpty';

import RequiredAsterisk from './RequiredAsterisk';

import {
    updateClaimAFacilityContactPerson,
    updateClaimAFacilityPhoneNumber,
    updateClaimAFacilityJobTitle,
} from '../actions/claimFacility.js';

import { getValueFromEvent } from '../util/util';

import { claimAFacilityFormStyles } from '../util/styles';

import { claimAFacilityFormFields } from '../util/constants';

const {
    contactName,
    contactEmail,
    contactPhone,
    contactJobTitle,
} = claimAFacilityFormFields;

const ClaimFacilityContactInfoStep = ({
    contactPerson,
    updateContactPerson,
    email,
    phoneNumber,
    updatePhoneNumber,
    fetching,
    jobTitle,
    updateJobTitle,
}) => (
    <>
        <div style={claimAFacilityFormStyles.inputGroupStyles}>
            <InputLabel htmlFor={contactName.id}>
                <Typography variant="title">
                    {contactName.label}
                    <RequiredAsterisk />
                </Typography>
            </InputLabel>
            <TextField
                autoFocus
                error={isEmpty(contactPerson)}
                id={contactName.id}
                variant="outlined"
                style={claimAFacilityFormStyles.textFieldStyles}
                value={contactPerson}
                onChange={updateContactPerson}
                disabled={fetching}
            />
        </div>
        <div style={claimAFacilityFormStyles.inputGroupStyles}>
            <InputLabel htmlFor={contactJobTitle.id}>
                <Typography variant="title">
                    {contactJobTitle.label}
                    <RequiredAsterisk />
                </Typography>
            </InputLabel>
            <TextField
                error={isEmpty(jobTitle)}
                id={contactJobTitle.id}
                variant="outlined"
                style={claimAFacilityFormStyles.textFieldStyles}
                value={jobTitle}
                onChange={updateJobTitle}
                disabled={fetching}
            />
        </div>
        <div style={claimAFacilityFormStyles.inputGroupStyles}>
            <InputLabel htmlFor={contactEmail.id}>
                <Typography variant="title">{contactEmail.label}</Typography>
            </InputLabel>
            <TextField
                id={contactEmail.id}
                variant="outlined"
                style={claimAFacilityFormStyles.textFieldStyles}
                defaultValue={email}
                InputProps={{
                    readOnly: true,
                }}
            />
            <Typography variant="subheading">
                Email on your account will be used by default
            </Typography>
        </div>
        <div style={claimAFacilityFormStyles.inputGroupStyles}>
            <InputLabel htmlFor={contactPhone.id}>
                <Typography variant="title">
                    {contactPhone.label}
                    <RequiredAsterisk />
                </Typography>
            </InputLabel>
            <TextField
                error={isEmpty(phoneNumber)}
                id={contactPhone.id}
                variant="outlined"
                style={claimAFacilityFormStyles.textFieldStyles}
                value={phoneNumber}
                onChange={updatePhoneNumber}
                disabled={fetching}
            />
        </div>
    </>
);

ClaimFacilityContactInfoStep.propTypes = {
    contactPerson: string.isRequired,
    email: string.isRequired,
    phoneNumber: string.isRequired,
    fetching: bool.isRequired,
    updateContactPerson: func.isRequired,
    updatePhoneNumber: func.isRequired,
    jobTitle: string.isRequired,
    updateJobTitle: func.isRequired,
};

const mapStateToProps = ({
    claimFacility: {
        claimData: {
            formData: { contactPerson, phoneNumber, jobTitle },
            fetching,
        },
    },
    auth: {
        user: {
            user: { email },
        },
    },
}) => ({
    contactPerson,
    email,
    phoneNumber,
    fetching,
    jobTitle,
});

const mapDispatchToProps = dispatch => ({
    updateContactPerson: e =>
        dispatch(updateClaimAFacilityContactPerson(getValueFromEvent(e))),
    updatePhoneNumber: e =>
        dispatch(updateClaimAFacilityPhoneNumber(getValueFromEvent(e))),
    updateJobTitle: e =>
        dispatch(updateClaimAFacilityJobTitle(getValueFromEvent(e))),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimFacilityContactInfoStep);
