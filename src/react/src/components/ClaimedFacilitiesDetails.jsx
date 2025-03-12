import React, { useEffect, useState } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, string } from 'prop-types';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
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
import checkComponentStatus from '../util/checkComponentStatus';
import InputSection from '../components/InputSection';

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
import { commonClaimFacilityFormStyles } from '../util/styles';

import apiRequest from '../util/apiRequest';

import {
    getValueFromEvent,
    getCheckedFromEvent,
    mapDjangoChoiceTuplesToSelectOptions,
    isValidFacilityURL,
    makeClaimGeocoderURL,
    logErrorToRollbar,
    isValidNumberOfWorkers,
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

    const { LoadingIndicator, AuthNotice, ErrorsList } = checkComponentStatus;
    if (fetching) {
        return <LoadingIndicator title={TITLE} />;
    }

    if (!userHasSignedIn) {
        return <AuthNotice title={TITLE} />;
    }

    if (errors) {
        return <ErrorsList title={TITLE} errors={errors} />;
    }

    if (!data) {
        return null;
    }

    const countryOptions = createCountrySelectOptions(data.countries);

    return (
        <AppOverflow>
            <AppGrid title="">
                <div
                    style={
                        commonClaimFacilityFormStyles.containerStylesWithPadding
                    }
                >
                    <div style={commonClaimFacilityFormStyles.formStyles}>
                        <Typography
                            variant="title"
                            style={commonClaimFacilityFormStyles.headingStyles}
                        >
                            Facility Details
                        </Typography>
                        <InputSection
                            label="Facility name (native language)"
                            value={data.facility_name_native_language}
                            onChange={updateFacilityNameNativeLanguage}
                            disabled={updating}
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
                        />
                        <InputSection
                            label="Description"
                            value={data.facility_description}
                            multiline
                            onChange={updateFacilityDescription}
                            disabled={updating}
                            classes={commonClaimFacilityFormStyles}
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
                                classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
                        />
                        <InputSection
                            label="Average lead time"
                            value={data.facility_average_lead_time}
                            onChange={updateFacilityAverageLeadTime}
                            disabled={updating}
                            classes={commonClaimFacilityFormStyles}
                        />
                        <InputSection
                            label="Number of workers"
                            value={data.facility_workers_count}
                            onChange={updateFacilityWorkersCount}
                            disabled={updating}
                            hasValidationErrorFn={() =>
                                !isValidNumberOfWorkers(
                                    data.facility_workers_count,
                                )
                            }
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
                        />
                        <Typography
                            variant="title"
                            style={commonClaimFacilityFormStyles.headingStyles}
                        >
                            Point of contact{' '}
                            <span
                                style={
                                    commonClaimFacilityFormStyles.switchSectionStyles
                                }
                            >
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
                            classes={commonClaimFacilityFormStyles}
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
                            classes={commonClaimFacilityFormStyles}
                        />
                        <Typography
                            variant="headline"
                            style={commonClaimFacilityFormStyles.headingStyles}
                        >
                            Office information{' '}
                            <span
                                style={
                                    commonClaimFacilityFormStyles.switchSectionStyles
                                }
                            >
                                <Switch
                                    color="primary"
                                    onChange={updateOfficeVisibility}
                                    checked={data.office_info_publicly_visible}
                                />
                                Publicly visible
                            </span>
                        </Typography>
                        <aside
                            style={commonClaimFacilityFormStyles.asideStyles}
                        >
                            If different from facility address
                        </aside>
                        <InputSection
                            label="Office name"
                            value={data.office_official_name}
                            onChange={updateOfficeName}
                            disabled={updating}
                            classes={commonClaimFacilityFormStyles}
                        />
                        <InputSection
                            label="Address"
                            value={data.office_address}
                            onChange={updateOfficeAddress}
                            disabled={updating}
                            classes={commonClaimFacilityFormStyles}
                        />
                        <InputSection
                            label="Country"
                            value={data.office_country_code}
                            onChange={updateOfficeCountry}
                            disabled={updating}
                            isSelect
                            selectOptions={countryOptions || []}
                            classes={commonClaimFacilityFormStyles}
                        />
                        <InputSection
                            label="Phone number"
                            value={data.office_phone_number}
                            onChange={updateOfficePhone}
                            disabled={updating}
                            classes={commonClaimFacilityFormStyles}
                        />
                        {errorUpdating && (
                            <div
                                style={
                                    commonClaimFacilityFormStyles.errorStyles
                                }
                            >
                                <Typography variant="body1">
                                    <span style={{ color: 'red' }}>
                                        The following errors prevented updating
                                        the facility claim:
                                    </span>
                                </Typography>
                                <ul>
                                    {errorUpdating.map(err => (
                                        <li key={err}>
                                            <span style={{ color: 'red' }}>
                                                {err}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        <div
                            style={commonClaimFacilityFormStyles.controlStyles}
                        >
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
)(ClaimedFacilitiesDetails);
