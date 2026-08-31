import React, { useEffect, useState } from 'react';
import { arrayOf, bool, func, object, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';

import ContactInfoStep from '../InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/ContactInfoStep';
import BusinessStep from '../InitialClaimFlow/ClaimForm/Steps/BusinessStep/BusinessStep';
import ProfileStep from '../InitialClaimFlow/ClaimForm/Steps/ProfileStep/ProfileStep';
import PendingClaimAttachments from './PendingClaimAttachments';
import SubmissionErrorsBanner from '../InitialClaimFlow/ClaimForm/SubmissionErrorsBanner/SubmissionErrorsBanner';

import {
    contactStepSchema,
    businessStepSchema,
    profileStepSchema,
} from '../InitialClaimFlow/ClaimForm/validationSchemas';
import { getTouchedFieldsFromErrors } from '../InitialClaimFlow/ClaimForm/utils';

import {
    fetchPendingClaim,
    savePendingClaim,
    deletePendingClaimAttachment,
    updatePendingClaimFormField,
    resetPendingClaimEdit,
} from '../../actions/pendingClaimEdit';
import {
    fetchCountryOptions,
    fetchFacilityProcessingTypeOptions,
} from '../../actions/filterOptions';
import {
    fetchProductionLocationByOsId,
    resetSingleProductionLocation,
} from '../../actions/contributeProductionLocation';

import { claimedFacilitiesRoute } from '../../util/constants';

const pendingClaimEditStyles = Object.freeze({
    container: Object.freeze({
        maxWidth: '960px',
        margin: '0 auto',
        padding: '20px',
    }),
    header: Object.freeze({
        margin: '10px 0',
    }),
    subtitle: Object.freeze({
        marginBottom: '20px',
    }),
    section: Object.freeze({
        padding: '25px',
        marginBottom: '20px',
    }),
    buttons: Object.freeze({
        display: 'flex',
        justifyContent: 'flex-end',
        gap: '10px',
        marginTop: '20px',
    }),
    loader: Object.freeze({
        display: 'block',
        margin: '40px auto',
    }),
});

// The full edit page validates every section at once; the two document
// picker fields are relaxed because already-uploaded attachments (shown
// in the attachments section) satisfy the documentation requirement.
const editValidationSchema = contactStepSchema
    .concat(businessStepSchema)
    .concat(profileStepSchema)
    .shape({
        employmentVerificationDocuments: Yup.array().notRequired(),
        companyAddressVerificationDocuments: Yup.array().notRequired(),
    });

function PendingClaimEdit({
    classes,
    match: {
        params: { claimID },
    },
    history: { push },
    data,
    fetching,
    error,
    formData,
    saving,
    savingError,
    deletingAttachment,
    getPendingClaim,
    saveClaim,
    deleteAttachment,
    updateFormField,
    resetState,
    prefetchCountries,
    prefetchProcessingTypes,
    prefetchProductionLocation,
    resetProductionLocation,
    countriesOptions,
    facilityProcessingTypeOptions,
}) {
    const [emissionsHasErrors, setEmissionsHasErrors] = useState(false);

    useEffect(() => {
        getPendingClaim(claimID);
        return () => {
            resetState();
            resetProductionLocation();
        };
    }, [claimID, getPendingClaim, resetState, resetProductionLocation]);

    useEffect(() => {
        if (!countriesOptions) {
            prefetchCountries();
        }
        if (!facilityProcessingTypeOptions) {
            prefetchProcessingTypes();
        }
    }, [
        countriesOptions,
        facilityProcessingTypeOptions,
        prefetchCountries,
        prefetchProcessingTypes,
    ]);

    useEffect(() => {
        if (data?.os_id) {
            prefetchProductionLocation(data.os_id);
        }
    }, [data?.os_id, prefetchProductionLocation]);

    const formik = useFormik({
        initialValues: formData || {},
        validationSchema: editValidationSchema,
        enableReinitialize: true,
        validateOnChange: true,
        validateOnBlur: true,
        onSubmit: () => saveClaim(claimID),
    });

    const handleFieldChange = (field, value) => {
        formik.setFieldValue(field, value, true);
        formik.setFieldTouched(field, true, false);
        updateFormField({ field, value });
    };

    const updateFieldWithoutTouch = (field, value) => {
        formik.setFieldValue(field, value, true);
        updateFormField({ field, value });
    };

    const handleBlur = field => formik.setFieldTouched(field, true, true);

    const handleSave = async () => {
        const errors = await formik.validateForm();
        if (Object.keys(errors).length > 0) {
            formik.setTouched(getTouchedFieldsFromErrors(errors));
            return;
        }
        formik.handleSubmit();
    };

    if (fetching) {
        return <CircularProgress className={classes.loader} />;
    }

    if (error || !data || !formData) {
        return (
            <div className={classes.container}>
                <Typography variant="title" className={classes.header}>
                    This claim is not available for editing
                </Typography>
                <Typography variant="body1">
                    It may have already been reviewed, or it may not belong to
                    your account. Only pending claims can be edited.
                </Typography>
                <Link to={claimedFacilitiesRoute} href={claimedFacilitiesRoute}>
                    Back to My Facilities
                </Link>
            </div>
        );
    }

    const stepProps = {
        formData: formik.values,
        handleChange: handleFieldChange,
        handleBlur,
        updateFieldWithoutTouch,
        errors: formik.errors,
        touched: formik.touched,
    };

    return (
        <div className={`${classes.container} notranslate`} translate="no">
            <Typography variant="title" className={classes.header}>
                Edit your pending claim
            </Typography>
            <Typography variant="body1" className={classes.subtitle}>
                {data.facility_name} ({data.os_id}) — submitted{' '}
                {new Date(data.created_at).toLocaleDateString()}. Your claim is
                awaiting review; any updates you save here are visible to the
                Open Supply Hub Claims Team.
            </Typography>

            <PendingClaimAttachments
                claimId={data.id}
                attachments={data.attachments}
                deleting={deletingAttachment}
                onDelete={attachmentID =>
                    deleteAttachment(claimID, attachmentID)
                }
            />

            <form>
                <Paper className={classes.section}>
                    <Typography variant="title">Contact information</Typography>
                    <ContactInfoStep {...stepProps} />
                </Paper>
                <Paper className={classes.section}>
                    <Typography variant="title">
                        Business information
                    </Typography>
                    <BusinessStep {...stepProps} />
                </Paper>
                <Paper className={classes.section}>
                    <Typography variant="title">
                        Production location profile
                    </Typography>
                    <ProfileStep
                        {...stepProps}
                        countryOptions={countriesOptions}
                        processingTypeOptions={facilityProcessingTypeOptions}
                        onEmissionsValidationChange={setEmissionsHasErrors}
                    />
                </Paper>

                <SubmissionErrorsBanner errors={savingError} />

                <div className={classes.buttons}>
                    <Button
                        variant="outlined"
                        onClick={() => push(claimedFacilitiesRoute)}
                        disabled={saving}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSave}
                        disabled={saving || emissionsHasErrors}
                    >
                        {saving ? (
                            <CircularProgress size={20} />
                        ) : (
                            'Save changes'
                        )}
                    </Button>
                </div>
            </form>
        </div>
    );
}

PendingClaimEdit.defaultProps = {
    data: null,
    error: null,
    formData: null,
    savingError: null,
    countriesOptions: null,
    facilityProcessingTypeOptions: null,
};

PendingClaimEdit.propTypes = {
    classes: object.isRequired,
    match: shape({
        params: shape({ claimID: string.isRequired }).isRequired,
    }).isRequired,
    history: shape({ push: func.isRequired }).isRequired,
    data: object,
    fetching: bool.isRequired,
    error: arrayOf(string),
    formData: object,
    saving: bool.isRequired,
    savingError: arrayOf(string),
    deletingAttachment: bool.isRequired,
    getPendingClaim: func.isRequired,
    saveClaim: func.isRequired,
    deleteAttachment: func.isRequired,
    updateFormField: func.isRequired,
    resetState: func.isRequired,
    prefetchCountries: func.isRequired,
    prefetchProcessingTypes: func.isRequired,
    prefetchProductionLocation: func.isRequired,
    resetProductionLocation: func.isRequired,
    countriesOptions: arrayOf(object),
    facilityProcessingTypeOptions: arrayOf(object),
};

const mapStateToProps = ({
    pendingClaimEdit: {
        data,
        fetching,
        error,
        formData,
        saving,
        savingError,
        deletingAttachment,
    },
    filterOptions: {
        countries: { data: countriesOptions },
        facilityProcessingType: { data: facilityProcessingTypeOptions },
    },
}) => ({
    data,
    fetching,
    error,
    formData,
    saving,
    savingError,
    deletingAttachment,
    countriesOptions,
    facilityProcessingTypeOptions,
});

const mapDispatchToProps = dispatch => ({
    getPendingClaim: claimID => dispatch(fetchPendingClaim(claimID)),
    saveClaim: claimID => dispatch(savePendingClaim(claimID)),
    deleteAttachment: (claimID, attachmentID) =>
        dispatch(deletePendingClaimAttachment(claimID, attachmentID)),
    updateFormField: payload => dispatch(updatePendingClaimFormField(payload)),
    resetState: () => dispatch(resetPendingClaimEdit()),
    prefetchCountries: () => dispatch(fetchCountryOptions()),
    prefetchProcessingTypes: () =>
        dispatch(fetchFacilityProcessingTypeOptions()),
    prefetchProductionLocation: osID =>
        dispatch(fetchProductionLocationByOsId(osID)),
    resetProductionLocation: () => dispatch(resetSingleProductionLocation()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(pendingClaimEditStyles)(PendingClaimEdit));
