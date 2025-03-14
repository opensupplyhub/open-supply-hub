import React, { useEffect, useState } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Switch from '@material-ui/core/Switch';
import flow from 'lodash/flow';
import noop from 'lodash/noop';
import memoize from 'lodash/memoize';
import isEmpty from 'lodash/isEmpty';
import get from 'lodash/get';
import map from 'lodash/map';
import { isEmail, isInt } from 'validator';
import { toast } from 'react-toastify';
import AppOverflow from './AppOverflow';
import AppGrid from './AppGrid';
import ClaimedFacilitiesDetailsSidebar from './ClaimedFacilitiesDetailsSidebar';
import ShowOnly from './ShowOnly';
import {
    LoadingIndicator,
    AuthNotice,
    ErrorsList,
} from './CheckComponentStatus';
import InputSection from '../components/InputSection';
import InputErrorText from '../components/Contribute/InputErrorText';

import {
    fetchClaimedFacilityDetails,
    clearClaimedFacilityDetails,
    updateClaimedFacilityNameNativeLanguage,
    updateClaimedFacilityWorkersCount,
    updateClaimedFacilityFemaleWorkersPercentage,
    updateClaimedFacilityAffiliations,
    updateClaimedFacilityCertifications,
    updateClaimedFacilityProductTypes,
    updateClaimedFacilityProductionTypes,
    updateClaimedFacilityLocation,
    updateClaimedSector,
    updateClaimedFacilityPhone,
    updateClaimedFacilityPhoneVisibility,
    updateClaimedFacilityParentCompany,
    updateClaimedFacilityWebsite,
    updateClaimedFacilityWebsiteVisibility,
    updateClaimedFacilityDescription,
    updateClaimedFacilityMinimumOrder,
    updateClaimedFacilityAverageLeadTime,
    updateClaimedFacilityContactPersonName,
    updateClaimedFacilityContactEmail,
    updateClaimedFacilityPointOfContactVisibility,
    updateClaimedFacilityOfficeVisibility,
    updateClaimedFacilityOfficeName,
    updateClaimedFacilityOfficeAddress,
    updateClaimedFacilityOfficeCountry,
    updateClaimedFacilityOfficePhone,
    submitClaimedFacilityDetailsUpdate,
} from '../actions/claimedFacilityDetails';

import {
    fetchParentCompanyOptions,
    fetchSectorOptions,
} from '../actions/filterOptions';

import {
    approvedFacilityClaimPropType,
    parentCompanyOptionsPropType,
    sectorOptionsPropType,
    userPropType,
} from '../util/propTypes';

import {
    claimedFacilitiesDetailsStyles,
    textFieldErrorStyles,
} from '../util/styles';

import apiRequest from '../util/apiRequest';

import {
    getValueFromEvent,
    getCheckedFromEvent,
    mapDjangoChoiceTuplesToSelectOptions,
    isValidFacilityURL,
    makeClaimGeocoderURL,
    logErrorToRollbar,
    isValidNumberOfWorkers,
    getNumberOfWorkersValidationError,
} from '../util/util';

import {
    claimAFacilityFormFields,
    USER_DEFAULT_STATE,
} from '../util/constants';

const {
    parentCompany: { aside: parentCompanyAside },
} = claimAFacilityFormFields;

const createCountrySelectOptions = memoize(
    mapDjangoChoiceTuplesToSelectOptions,
);

const mergedStyles = {
    ...claimedFacilitiesDetailsStyles(),
    ...textFieldErrorStyles(),
};
function ClaimedFacilitiesDetails({
    user,
    match: {
        params: { claimID },
    },
    fetching,
    errors,
    data,
    getDetails,
    clearDetails,
    updateFacilityNameNativeLanguage,
    updateFacilityLocation,
    updateSector,
    updateFacilityPhone,
    updateFacilityWebsite,
    updateFacilityWebsiteVisibility,
    updateFacilityDescription,
    updateFacilityMinimumOrder,
    updateFacilityAverageLeadTime,
    updateFacilityWorkersCount,
    updateFacilityFemaleWorkersPercentage,
    updateFacilityAffiliations,
    updateFacilityCertifications,
    updateFacilityProductTypes,
    updateFacilityProductionTypes,
    updateContactPerson,
    updateContactEmail,
    updateOfficeName,
    updateOfficeAddress,
    updateOfficeCountry,
    updateOfficePhone,
    submitUpdate,
    updating,
    updateFacilityPhoneVisibility,
    updateContactVisibility,
    updateOfficeVisibility,
    errorUpdating,
    updateParentCompany,
    sectorOptions,
    parentCompanyOptions,
    fetchSectors,
    fetchParentCompanies,
    userHasSignedIn,
    classes,
}) {
    /* eslint-disable react-hooks/exhaustive-deps */
    // disabled because we want to use this as just
    // componentDidMount and componentWillUpdate and declaring the
    // methods in the array here caused an infinite loop for some reason
    useEffect(() => {
        getDetails();

        return clearDetails;
    }, []);
    /* eslint-enable react-hooks/exhaustive-deps */
    useEffect(() => {
        if (!parentCompanyOptions) {
            fetchParentCompanies();
        }
    }, [parentCompanyOptions, fetchParentCompanies]);
    useEffect(() => {
        if (!sectorOptions) {
            fetchSectors();
        }
    }, [sectorOptions, fetchSectors]);

    const [isSavingForm, setIsSavingForm] = useState(false);
    const TITLE = 'Claimed Facility Details';

    useEffect(() => {
        if (updating || errorUpdating) {
            noop();
        }

        if (!updating && isSavingForm) {
            setIsSavingForm(false);

            if (!errorUpdating) {
                toast('Claimed facility profile was saved');
            }
        }
    }, [isSavingForm, setIsSavingForm, updating, errorUpdating]);

    const geocodeDataToGeoJSON = geocodedData => ({
        type: 'Point',
        coordinates: [
            geocodedData.geocoded_point.lng,
            geocodedData.geocoded_point.lat,
        ],
    });

    const geocodeAddress = (address, initialAddress, initialLocation) => {
        if (isEmpty(address)) {
            return Promise.resolve(null);
        }
        if (address === initialAddress && initialLocation) {
            return Promise.resolve(initialLocation);
        }
        return apiRequest
            .get(makeClaimGeocoderURL(claimID), {
                params: {
                    address,
                },
            })
            .then(({ data: geocodedData }) => {
                if (geocodedData?.result_count === 0) {
                    return Promise.reject(
                        new Error(
                            'There was a problem finding a location for the specified address',
                        ),
                    );
                }
                return geocodeDataToGeoJSON(geocodedData);
            });
    };

    const saveForm = () => {
        geocodeAddress(
            data.facility_address,
            data.initial_facility_address,
            data.facility_location,
        )
            .then(location => {
                updateFacilityLocation(location);
                submitUpdate();
                setIsSavingForm(true);
            })
            .catch(err => {
                toast.error(
                    'There was a problem finding a location for the specified address',
                );
                logErrorToRollbar(window, err, user);
            });
    };

    if (fetching) {
        return <LoadingIndicator title={TITLE} />;
    }

    if (!userHasSignedIn) {
        return <AuthNotice title={TITLE} />;
    }

    if (errors && errors.length > 0) {
        return <ErrorsList title={TITLE} errors={errors} />;
    }

    if (!data) {
        return null;
    }

    const countryOptions = createCountrySelectOptions(data.countries);

    return (
        <AppOverflow>
            <AppGrid title={TITLE}>
                <div className={classes.containerStyles}>
                    <div className={classes.widthStyle}>
                        <Typography variant="title">
                            Facility Details
                        </Typography>
                        <InputSection
                            label="Facility name (native language)"
                            value={data.facility_name_native_language}
                            onChange={updateFacilityNameNativeLanguage}
                            disabled={updating}
                        />
                        <InputSection
                            label="Sector"
                            value={get(data, 'sector', [])}
                            onChange={updateSector}
                            disabled={updating}
                            isSelect
                            isMultiSelect
                            selectOptions={sectorOptions || []}
                            selectPlaceholder="Select..."
                        />
                        <InputSection
                            label="Phone Number"
                            value={data.facility_phone_number}
                            onChange={updateFacilityPhone}
                            disabled={updating}
                            hasSwitch
                            switchValue={
                                data.facility_phone_number_publicly_visible
                            }
                            onSwitchChange={updateFacilityPhoneVisibility}
                        />
                        <InputSection
                            label="Website"
                            value={data.facility_website}
                            onChange={updateFacilityWebsite}
                            disabled={updating}
                            hasValidationErrorFn={() => {
                                if (isEmpty(data.facility_website)) {
                                    return false;
                                }

                                return !isValidFacilityURL(
                                    data.facility_website,
                                );
                            }}
                            hasSwitch
                            switchValue={data.facility_website_publicly_visible}
                            onSwitchChange={updateFacilityWebsiteVisibility}
                        />
                        <InputSection
                            label="Description"
                            value={data.facility_description}
                            multiline
                            onChange={updateFacilityDescription}
                            disabled={updating}
                        />
                        <ShowOnly when={!isEmpty(parentCompanyOptions)}>
                            <InputSection
                                isCreatable
                                label="Parent Company / Supplier Group"
                                aside={parentCompanyAside}
                                value={get(
                                    data,
                                    'facility_parent_company.id',
                                    null,
                                )}
                                onChange={updateParentCompany}
                                disabled={updating}
                                isSelect
                                selectOptions={parentCompanyOptions}
                            />
                        </ShowOnly>
                        <ShowOnly when={!parentCompanyOptions}>
                            <Typography>
                                Parent Company / Supplier Group
                            </Typography>
                            <Typography>
                                {get(
                                    data,
                                    'facility_parent_company.name',
                                    null,
                                )}
                            </Typography>
                        </ShowOnly>
                        <InputSection
                            label="Minimum order quantity"
                            value={data.facility_minimum_order_quantity}
                            onChange={updateFacilityMinimumOrder}
                            disabled={updating}
                        />
                        <InputSection
                            label="Average lead time"
                            value={data.facility_average_lead_time}
                            onChange={updateFacilityAverageLeadTime}
                            disabled={updating}
                        />
                        <Typography
                            component="h2"
                            className={classes.titleStyles}
                        >
                            Number of Workers
                        </Typography>
                        <TextField
                            variant="outlined"
                            className={classes.textInputStyles}
                            value={data.facility_workers_count}
                            onChange={updateFacilityWorkersCount}
                            disabled={updating}
                            error={
                                !isValidNumberOfWorkers(
                                    data.facility_workers_count,
                                )
                            }
                            helperText={
                                !isValidNumberOfWorkers(
                                    data.facility_workers_count,
                                ) && (
                                    <InputErrorText
                                        text={getNumberOfWorkersValidationError(
                                            data.facility_workers_count,
                                        )}
                                    />
                                )
                            }
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                            InputProps={{
                                classes: {
                                    input: `
                                ${
                                    !isValidNumberOfWorkers(
                                        data.facility_workers_count,
                                    ) && classes.errorStyle
                                }`,
                                },
                            }}
                        />
                        <InputSection
                            label="Percentage of female workers"
                            value={data.facility_female_workers_percentage}
                            onChange={updateFacilityFemaleWorkersPercentage}
                            disabled={updating}
                            hasValidationErrorFn={() => {
                                if (
                                    isEmpty(
                                        data.facility_female_workers_percentage,
                                    )
                                ) {
                                    return false;
                                }

                                return !isInt(
                                    data.facility_female_workers_percentage,
                                    {
                                        min: 0,
                                        max: 100,
                                    },
                                );
                            }}
                        />
                        <InputSection
                            label="Affiliations"
                            value={get(data, 'facility_affiliations', [])}
                            onChange={updateFacilityAffiliations}
                            disabled={updating}
                            isSelect
                            isMultiSelect
                            selectOptions={mapDjangoChoiceTuplesToSelectOptions(
                                data.affiliation_choices,
                            )}
                        />
                        <InputSection
                            label="Certifications/Standards/Regulations"
                            value={get(data, 'facility_certifications', [])}
                            onChange={updateFacilityCertifications}
                            disabled={updating}
                            isSelect
                            isMultiSelect
                            selectOptions={mapDjangoChoiceTuplesToSelectOptions(
                                data.certification_choices,
                            )}
                        />
                        <InputSection
                            label="Facility / Processing Types"
                            value={get(data, 'facility_production_types', [])}
                            onChange={updateFacilityProductionTypes}
                            disabled={updating}
                            isSelect
                            isMultiSelect
                            selectOptions={mapDjangoChoiceTuplesToSelectOptions(
                                data.production_type_choices,
                            )}
                        />
                        <InputSection
                            label="Product Types"
                            value={get(data, 'facility_product_types', [])}
                            onChange={updateFacilityProductTypes}
                            disabled={updating}
                            isSelect
                            isMultiSelect
                            isCreatable
                            selectPlaceholder="e.g. Jackets - Use <Enter> or <Tab> to add multiple values"
                        />
                        <Typography
                            variant="title"
                            className={classes.headingStyles}
                        >
                            Point of contact{' '}
                            <span className={classes.switchSectionStyles}>
                                <Switch
                                    color="primary"
                                    onChange={updateContactVisibility}
                                    checked={
                                        data.point_of_contact_publicly_visible
                                    }
                                />
                                Publicly visible
                            </span>
                        </Typography>
                        <InputSection
                            label="Contact person name"
                            value={data.point_of_contact_person_name}
                            onChange={updateContactPerson}
                            disabled={updating}
                        />
                        <InputSection
                            label="Email"
                            value={data.point_of_contact_email}
                            onChange={updateContactEmail}
                            disabled={updating}
                            hasValidationErrorFn={() => {
                                if (isEmpty(data.point_of_contact_email)) {
                                    return false;
                                }

                                return !isEmail(data.point_of_contact_email);
                            }}
                        />
                        <Typography
                            variant="headline"
                            className={classes.headingStyles}
                        >
                            Office information{' '}
                            <span className={classes.switchSectionStyles}>
                                <Switch
                                    color="primary"
                                    onChange={updateOfficeVisibility}
                                    checked={data.office_info_publicly_visible}
                                />
                                Publicly visible
                            </span>
                        </Typography>
                        <aside className={classes.asideStyles}>
                            If different from facility address
                        </aside>
                        <InputSection
                            label="Office name"
                            value={data.office_official_name}
                            onChange={updateOfficeName}
                            disabled={updating}
                        />
                        <InputSection
                            label="Address"
                            value={data.office_address}
                            onChange={updateOfficeAddress}
                            disabled={updating}
                        />
                        <InputSection
                            label="Country"
                            value={data.office_country_code}
                            onChange={updateOfficeCountry}
                            disabled={updating}
                            isSelect
                            selectOptions={countryOptions || []}
                        />
                        <InputSection
                            label="Phone number"
                            value={data.office_phone_number}
                            onChange={updateOfficePhone}
                            disabled={updating}
                        />
                        {errorUpdating && (
                            <div className={classes.errorStyles}>
                                <Typography variant="body1">
                                    <span className={classes.errorTextStyle}>
                                        The following errors prevented updating
                                        the facility claim:
                                    </span>
                                </Typography>
                                <ul>
                                    {errorUpdating.map(err => (
                                        <li key={err}>
                                            <span
                                                className={
                                                    classes.errorTextStyle
                                                }
                                            >
                                                {err}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        <div className={classes.controlStyles}>
                            <Button
                                onClick={saveForm}
                                variant="contained"
                                color="primary"
                                disabled={
                                    updating ||
                                    (!isEmpty(data.point_of_contact_email) &&
                                        !isEmail(
                                            data.point_of_contact_email,
                                        )) ||
                                    (!isEmpty(data.facility_website) &&
                                        !isValidFacilityURL(
                                            data.facility_website,
                                        )) ||
                                    !isValidNumberOfWorkers(
                                        data.facility_workers_count,
                                    )
                                }
                            >
                                Save
                            </Button>
                            {updating && <CircularProgress />}
                        </div>
                    </div>
                    <ClaimedFacilitiesDetailsSidebar
                        facilityDetails={data.facility}
                    />
                </div>
            </AppGrid>
        </AppOverflow>
    );
}

ClaimedFacilitiesDetails.defaultProps = {
    user: USER_DEFAULT_STATE,
    errors: null,
    data: null,
    errorUpdating: null,
    sectorOptions: null,
    parentCompanyOptions: null,
};

ClaimedFacilitiesDetails.propTypes = {
    user: userPropType,
    fetching: bool.isRequired,
    errors: arrayOf(string),
    data: approvedFacilityClaimPropType,
    getDetails: func.isRequired,
    clearDetails: func.isRequired,
    updateFacilityNameNativeLanguage: func.isRequired,
    updateFacilityWorkersCount: func.isRequired,
    updateFacilityFemaleWorkersPercentage: func.isRequired,
    updateFacilityPhone: func.isRequired,
    updateFacilityWebsite: func.isRequired,
    updateFacilityWebsiteVisibility: func.isRequired,
    updateFacilityDescription: func.isRequired,
    updateFacilityMinimumOrder: func.isRequired,
    updateFacilityAverageLeadTime: func.isRequired,
    updateContactPerson: func.isRequired,
    updateContactEmail: func.isRequired,
    updateOfficeName: func.isRequired,
    updateOfficeAddress: func.isRequired,
    updateOfficeCountry: func.isRequired,
    updateOfficePhone: func.isRequired,
    submitUpdate: func.isRequired,
    updating: bool.isRequired,
    errorUpdating: arrayOf(string),
    updateFacilityPhoneVisibility: func.isRequired,
    updateContactVisibility: func.isRequired,
    updateOfficeVisibility: func.isRequired,
    sectorOptions: sectorOptionsPropType,
    parentCompanyOptions: parentCompanyOptionsPropType,
    fetchSectors: func.isRequired,
    userHasSignedIn: bool.isRequired,
    classes: object.isRequired,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
    claimedFacilityDetails: {
        retrieveData: { fetching: fetchingData, error },
        updateData: { fetching: updating, error: errorUpdating },
        data,
    },
    filterOptions: {
        sectors: { data: sectorOptions, fetching: fetchingSectors },
        parentCompanies: {
            data: parentCompanyOptions,
            fetching: fetchingParentCompanies,
        },
    },
}) {
    return {
        user,
        fetching: fetchingData || fetchingSectors || fetchingParentCompanies,
        data,
        errors: error || errorUpdating,
        updating,
        errorUpdating,
        sectorOptions,
        parentCompanyOptions,
        userHasSignedIn: !user.isAnon,
    };
}

function mapDispatchToProps(
    dispatch,
    {
        match: {
            params: { claimID },
        },
    },
) {
    const makeDispatchValueFn = updateFn =>
        flow(getValueFromEvent, updateFn, dispatch);

    const makeDispatchCheckedFn = updateFn =>
        flow(getCheckedFromEvent, updateFn, dispatch);

    const makeDispatchMultiSelectFn = updateFn =>
        flow(selection => map(selection, 'value'), updateFn, dispatch);

    return {
        getDetails: () => dispatch(fetchClaimedFacilityDetails(claimID)),
        clearDetails: () => dispatch(clearClaimedFacilityDetails()),
        updateFacilityNameNativeLanguage: makeDispatchValueFn(
            updateClaimedFacilityNameNativeLanguage,
        ),
        updateFacilityLocation: location =>
            dispatch(updateClaimedFacilityLocation(location)),
        updateSector: makeDispatchMultiSelectFn(updateClaimedSector),
        updateFacilityPhone: makeDispatchValueFn(updateClaimedFacilityPhone),
        updateFacilityPhoneVisibility: makeDispatchCheckedFn(
            updateClaimedFacilityPhoneVisibility,
        ),
        updateParentCompany: ({ label, value }) =>
            dispatch(
                updateClaimedFacilityParentCompany({
                    id: value,
                    name: label,
                }),
            ),
        updateContactVisibility: makeDispatchCheckedFn(
            updateClaimedFacilityPointOfContactVisibility,
        ),
        updateOfficeVisibility: makeDispatchCheckedFn(
            updateClaimedFacilityOfficeVisibility,
        ),
        updateFacilityWebsite: makeDispatchValueFn(
            updateClaimedFacilityWebsite,
        ),
        updateFacilityWebsiteVisibility: makeDispatchCheckedFn(
            updateClaimedFacilityWebsiteVisibility,
        ),
        updateFacilityDescription: makeDispatchValueFn(
            updateClaimedFacilityDescription,
        ),
        updateFacilityMinimumOrder: makeDispatchValueFn(
            updateClaimedFacilityMinimumOrder,
        ),
        updateFacilityAverageLeadTime: makeDispatchValueFn(
            updateClaimedFacilityAverageLeadTime,
        ),
        updateFacilityWorkersCount: makeDispatchValueFn(
            updateClaimedFacilityWorkersCount,
        ),
        updateFacilityFemaleWorkersPercentage: makeDispatchValueFn(
            updateClaimedFacilityFemaleWorkersPercentage,
        ),
        updateFacilityAffiliations: makeDispatchMultiSelectFn(
            updateClaimedFacilityAffiliations,
        ),
        updateFacilityCertifications: makeDispatchMultiSelectFn(
            updateClaimedFacilityCertifications,
        ),
        updateFacilityProductTypes: makeDispatchMultiSelectFn(
            updateClaimedFacilityProductTypes,
        ),
        updateFacilityProductionTypes: makeDispatchMultiSelectFn(
            updateClaimedFacilityProductionTypes,
        ),
        updateContactPerson: makeDispatchValueFn(
            updateClaimedFacilityContactPersonName,
        ),
        updateContactEmail: makeDispatchValueFn(
            updateClaimedFacilityContactEmail,
        ),
        updateOfficeName: makeDispatchValueFn(updateClaimedFacilityOfficeName),
        updateOfficeAddress: makeDispatchValueFn(
            updateClaimedFacilityOfficeAddress,
        ),
        updateOfficeCountry: ({ value }) =>
            dispatch(updateClaimedFacilityOfficeCountry(value)),
        updateOfficePhone: makeDispatchValueFn(
            updateClaimedFacilityOfficePhone,
        ),
        submitUpdate: () =>
            dispatch(submitClaimedFacilityDetailsUpdate(claimID)),
        fetchSectors: () => dispatch(fetchSectorOptions()),
        fetchParentCompanies: () => dispatch(fetchParentCompanyOptions()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(mergedStyles)(ClaimedFacilitiesDetails));
