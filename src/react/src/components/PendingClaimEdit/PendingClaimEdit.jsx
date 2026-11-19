import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { arrayOf, bool, func, number, object, shape, string } from 'prop-types';
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
import ClaimOutcomeDialog from '../ClaimOutcomeDialog';
import ClaimLiveCheck from '../ClaimLiveCheck/ClaimLiveCheck';
import {
    CLAIM_LIVE_CHECK_FIELD_LABELS,
    makeFixBannerTitle,
    SAVE_AND_CHECK_AGAIN_BUTTON_TEXT,
} from '../ClaimLiveCheck/constants';
import { fixBannerStyles } from '../ClaimLiveCheck/styles';
import {
    focusFixField,
    getFixesByField,
    parseFixParams,
} from '../ClaimLiveCheck/utils';
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
    fetchClaimLiveCheckFixes,
    resetClaimLiveCheckFixes,
} from '../../actions/claimLiveCheck';
import {
    fetchCountryOptions,
    fetchFacilityProcessingTypeOptions,
} from '../../actions/filterOptions';
import {
    fetchProductionLocationByOsId,
    resetSingleProductionLocation,
} from '../../actions/contributeProductionLocation';

import {
    claimedFacilitiesRoute,
    mapRoute,
    CLAIM_LIVE_CHECK,
} from '../../util/constants';

const pendingClaimEditLayoutStyles = Object.freeze({
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

const pendingClaimEditStyles = theme =>
    Object.freeze({
        ...pendingClaimEditLayoutStyles,
        ...fixBannerStyles(theme),
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
    history,
    location,
    data,
    fetching,
    error,
    formData,
    saving,
    saved,
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
    isLiveCheckEnabled,
    liveCheckFixes,
    liveCheckFixesFetching,
    liveCheckChecksLeft,
    getLiveCheckFixes,
    resetLiveCheckFixes,
}) {
    const { push } = history;
    const [emissionsHasErrors, setEmissionsHasErrors] = useState(false);
    // A claimant who chose to go back and fix their claim on the live
    // check arrives with the field to scroll to first, and whether to
    // check again after saving, in the query string (OSDEV-3805).
    const search = location ? location.search : '';
    const locationKey = location ? location.key : undefined;
    const { fix, checkAgain } = useMemo(() => parseFixParams(search), [search]);
    // What is marked on the page does not come from the query string:
    // it is the claim's latest check, read from the API on every visit,
    // so it is the same from the result screen, the email link and My
    // Claims. The API returns no fixes once the claim has been edited
    // since that check. With the feature off, or without fixes, this
    // page behaves as it always has.
    const fixesByField = useMemo(
        () => (isLiveCheckEnabled ? getFixesByField(liveCheckFixes) : {}),
        [isLiveCheckEnabled, liveCheckFixes],
    );
    const flaggedFields = Object.keys(fixesByField);
    const fixCount = flaggedFields.reduce(
        (count, field) => count + fixesByField[field].length,
        0,
    );
    // Set when the check after a save could not be started; the save
    // then ends with the usual thank-you dialog.
    const [checkSkipped, setCheckSkipped] = useState(false);
    const skipCheck = useCallback(() => setCheckSkipped(true), []);
    const checksAfterSave =
        isLiveCheckEnabled &&
        !checkSkipped &&
        (checkAgain || (fixCount > 0 && liveCheckChecksLeft > 0));
    // Latched locally so a stray Redux state change can never close the
    // dialog once a save has succeeded; it closes only by navigating
    // away (both dialog actions navigate, and unmount resets the slice).
    const [outcomeDialogOpen, setOutcomeDialogOpen] = useState(false);

    useEffect(() => {
        if (saved) {
            setOutcomeDialogOpen(true);
        }
    }, [saved]);

    // Every visit starts clean, including coming back to this page
    // from the result of a check that ran here after a save.
    useEffect(() => {
        setOutcomeDialogOpen(false);
        setCheckSkipped(false);
        getPendingClaim(claimID);
        return () => {
            resetState();
            resetProductionLocation();
        };
    }, [
        claimID,
        locationKey,
        getPendingClaim,
        resetState,
        resetProductionLocation,
    ]);

    useEffect(() => {
        if (!isLiveCheckEnabled) {
            return undefined;
        }
        getLiveCheckFixes(claimID);
        return resetLiveCheckFixes;
    }, [
        isLiveCheckEnabled,
        claimID,
        locationKey,
        getLiveCheckFixes,
        resetLiveCheckFixes,
    ]);

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

    // The steps must not mount until the outer formik has actually
    // hydrated: enableReinitialize applies one render after formData
    // arrives, and EmissionsEstimateForm seeds its own internal Formik
    // from whatever it receives at mount (no reinitialize) — mounting
    // it against the pre-hydration empty values leaves the emissions
    // section blank and syncs '' back over the fetched data.
    const formHydrated = Object.keys(formik.values).length > 0;

    // Take the claimant to the field they came back to fix, once, as
    // soon as the form is on the page and its marks are known.
    const formReady =
        Boolean(data) && formHydrated && !fetching && !liveCheckFixesFetching;
    useEffect(() => {
        if (isLiveCheckEnabled && formReady && fix) {
            focusFixField(fix);
        }
    }, [isLiveCheckEnabled, formReady, fix]);

    // On the very first render data is null and fetching has not been
    // set yet (the fetch dispatch runs in an effect), so treat that as
    // loading too rather than flashing the not-available message.
    if (fetching || (!data && !error) || (data && !formHydrated)) {
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

    // The edit is saved; check the claim again in place of the usual
    // thank-you dialog.
    if (outcomeDialogOpen && checksAfterSave) {
        return (
            <div className={`${classes.container} notranslate`} translate="no">
                <Typography variant="title" className={classes.header}>
                    Edit your pending claim
                </Typography>
                <Paper className={classes.section}>
                    <ClaimLiveCheck
                        claimID={claimID}
                        history={history}
                        onNotStarted={skipCheck}
                    />
                </Paper>
            </div>
        );
    }

    const saveButtonText = checksAfterSave
        ? SAVE_AND_CHECK_AGAIN_BUTTON_TEXT
        : 'Save changes';

    const stepProps = {
        formData: formik.values,
        handleChange: handleFieldChange,
        handleBlur,
        updateFieldWithoutTouch,
        errors: formik.errors,
        touched: formik.touched,
        liveCheckFixes: fixesByField,
    };

    return (
        <>
            <div className={`${classes.container} notranslate`} translate="no">
                <Typography variant="title" className={classes.header}>
                    Edit your pending claim
                </Typography>
                <Typography variant="body1" className={classes.subtitle}>
                    {data.facility_name} ({data.os_id}) — submitted{' '}
                    {new Date(data.created_at).toLocaleDateString()}. Your claim
                    is awaiting review; any updates you save here are visible to
                    the Open Supply Hub Claims Team.
                </Typography>

                {fixCount > 0 && (
                    <div className={classes.banner} role="status">
                        <Typography
                            component="h2"
                            className={classes.bannerTitle}
                        >
                            {makeFixBannerTitle(fixCount)}
                        </Typography>
                        <ul className={classes.bannerLinks}>
                            {flaggedFields.map(field => (
                                <li key={field}>
                                    <Button
                                        className={classes.bannerLink}
                                        onClick={() =>
                                            focusFixField(
                                                fixesByField[field][0],
                                            )
                                        }
                                        disableRipple
                                    >
                                        {CLAIM_LIVE_CHECK_FIELD_LABELS[field]}
                                    </Button>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

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
                        <Typography variant="title">
                            Contact information
                        </Typography>
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
                            processingTypeOptions={
                                facilityProcessingTypeOptions
                            }
                            onEmissionsValidationChange={setEmissionsHasErrors}
                            emissionsFormData={formik.values}
                            onEmissionsValueChange={handleFieldChange}
                            onEmissionsEnabledChange={updateFieldWithoutTouch}
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
                                saveButtonText
                            )}
                        </Button>
                    </div>
                </form>
            </div>
            <ClaimOutcomeDialog
                open={outcomeDialogOpen}
                title="Thank you for editing your claim request!"
                body="We have received your edited claim request, we will review it shortly."
                actions={[
                    {
                        label: 'To My Claims',
                        onClick: () => push(claimedFacilitiesRoute),
                        secondary: true,
                    },
                    {
                        label: 'Search OS Hub',
                        onClick: () => push(mapRoute),
                    },
                ]}
            />
        </>
    );
}

PendingClaimEdit.defaultProps = {
    location: null,
    liveCheckFixes: [],
    liveCheckFixesFetching: false,
    liveCheckChecksLeft: 0,
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
    location: shape({ search: string, key: string }),
    isLiveCheckEnabled: bool.isRequired,
    liveCheckFixes: arrayOf(string),
    liveCheckFixesFetching: bool,
    liveCheckChecksLeft: number,
    getLiveCheckFixes: func.isRequired,
    resetLiveCheckFixes: func.isRequired,
    data: object,
    fetching: bool.isRequired,
    error: arrayOf(string),
    formData: object,
    saving: bool.isRequired,
    saved: bool.isRequired,
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
        saved,
        savingError,
        deletingAttachment,
    },
    filterOptions: {
        countries: { data: countriesOptions },
        facilityProcessingType: { data: facilityProcessingTypeOptions },
    },
    featureFlags: { flags },
    claimLiveCheckFixes: {
        fixes: liveCheckFixes,
        fetching: liveCheckFixesFetching,
        checksLeft: liveCheckChecksLeft,
    },
}) => ({
    isLiveCheckEnabled: !!flags[CLAIM_LIVE_CHECK],
    liveCheckFixes,
    liveCheckFixesFetching,
    liveCheckChecksLeft,
    data,
    fetching,
    error,
    formData,
    saving,
    saved,
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
    getLiveCheckFixes: claimID => dispatch(fetchClaimLiveCheckFixes(claimID)),
    resetLiveCheckFixes: () => dispatch(resetClaimLiveCheckFixes()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(pendingClaimEditStyles)(PendingClaimEdit));
