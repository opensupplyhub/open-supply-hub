import React, { useEffect, useMemo, useState } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Switch from '@material-ui/core/Switch';
import Checkbox from '@material-ui/core/Checkbox';
import Grid from '@material-ui/core/Grid';
import flow from 'lodash/flow';
import noop from 'lodash/noop';
import memoize from 'lodash/memoize';
import isEmpty from 'lodash/isEmpty';
import get from 'lodash/get';
import map from 'lodash/map';
import { isInt } from 'validator';
import { toast } from 'react-toastify';
import AppOverflow from '../AppOverflow';
import AppGrid from '../AppGrid';
import ClaimedFacilitiesDetailsSidebar from '../ClaimedFacilitiesDetailsSidebar';
import {
    LoadingIndicator,
    AuthNotice,
    ErrorsList,
} from '../CheckComponentStatus';
import InputSection from '../InputSection';
import InputErrorText from '../Contribute/InputErrorText';

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
    updateClaimedFacilityOpeningDate,
    updateClaimedFacilityClosingDate,
    updateClaimedEstimatedAnnualThroughput,
    updateClaimedEnergyCoal,
    updateClaimedEnergyNaturalGas,
    updateClaimedEnergyDiesel,
    updateClaimedEnergyKerosene,
    updateClaimedEnergyBiomass,
    updateClaimedEnergyCharcoal,
    updateClaimedEnergyAnimalWaste,
    updateClaimedEnergyElectricity,
    updateClaimedEnergyOther,
    updateClaimedEnergyCoalEnabled,
    updateClaimedEnergyNaturalGasEnabled,
    updateClaimedEnergyDieselEnabled,
    updateClaimedEnergyKeroseneEnabled,
    updateClaimedEnergyBiomassEnabled,
    updateClaimedEnergyCharcoalEnabled,
    updateClaimedEnergyAnimalWasteEnabled,
    updateClaimedEnergyElectricityEnabled,
    updateClaimedEnergyOtherEnabled,
    submitClaimedFacilityDetailsUpdate,
} from '../../actions/claimedFacilityDetails';

import {
    approvedFacilityClaimPropType,
    userPropType,
} from '../../util/propTypes';

import {
    claimedFacilitiesDetailsStyles,
    textFieldErrorStyles,
} from '../../util/styles';

import apiRequest from '../../util/apiRequest';

import {
    getValueFromEvent,
    getCheckedFromEvent,
    mapDjangoChoiceTuplesToSelectOptions,
    makeClaimGeocoderURL,
    logErrorToRollbar,
} from '../../util/util';

import { USER_DEFAULT_STATE, mockedSectors } from '../../util/constants';
import freeEmissionsEstimateValidationSchema from '../FreeEmissionsEstimate/utils';
import { freeEmissionsEstimateFormConfig } from '../FreeEmissionsEstimate/constants.jsx';
import YearPicker from '../FreeEmissionsEstimate/YearPicker.jsx';
import MonthYearPicker from '../FreeEmissionsEstimate/MonthYearPicker.jsx';
import claimedFacilityDetailsSchema from './validationSchema';

const createCountrySelectOptions = memoize(
    mapDjangoChoiceTuplesToSelectOptions,
);

const {
    openingDateField,
    closingDateField,
    estimatedAnnualThroughputField,
    energyConsumptionLabel,
    energySourcesData,
} = freeEmissionsEstimateFormConfig;

const mergedStyles = {
    ...claimedFacilitiesDetailsStyles(),
    ...textFieldErrorStyles(),
    paddedTitle: {
        padding: '10px 0',
    },
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
    updateOpeningDate,
    updateClosingDate,
    updateEstimatedAnnualThroughput,
    updateEnergyCoal,
    updateEnergyNaturalGas,
    updateEnergyDiesel,
    updateEnergyKerosene,
    updateEnergyBiomass,
    updateEnergyCharcoal,
    updateEnergyAnimalWaste,
    updateEnergyElectricity,
    updateEnergyOther,
    updateEnergyCoalEnabled,
    updateEnergyNaturalGasEnabled,
    updateEnergyDieselEnabled,
    updateEnergyKeroseneEnabled,
    updateEnergyBiomassEnabled,
    updateEnergyCharcoalEnabled,
    updateEnergyAnimalWasteEnabled,
    updateEnergyElectricityEnabled,
    updateEnergyOtherEnabled,
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

    const facilityData = data || {};

    const claimedValidationValues = useMemo(
        () => ({
            facility_website: facilityData.facility_website,
            point_of_contact_email: facilityData.point_of_contact_email,
            facility_workers_count: facilityData.facility_workers_count,
        }),
        [facilityData],
    );

    const claimedValidationErrors = useMemo(() => {
        try {
            claimedFacilityDetailsSchema.validateSync(claimedValidationValues, {
                abortEarly: false,
            });
            return {};
        } catch (validationError) {
            if (validationError?.inner?.length) {
                return validationError.inner.reduce((acc, err) => {
                    if (err.path) {
                        acc[err.path] = err.message;
                    }
                    return acc;
                }, {});
            }
            return {};
        }
    }, [claimedValidationValues]);

    const getClaimedValidationError = key => claimedValidationErrors[key];
    const hasClaimedValidationErrors = !isEmpty(claimedValidationErrors);

    const emissionsValidationValues = useMemo(
        () => ({
            openingDate: facilityData.opening_date,
            closingDate: facilityData.closing_date,
            estimatedAnnualThroughput: facilityData.estimated_annual_throughput,
            energyCoal: facilityData.energy_coal,
            energyNaturalGas: facilityData.energy_natural_gas,
            energyDiesel: facilityData.energy_diesel,
            energyKerosene: facilityData.energy_kerosene,
            energyBiomass: facilityData.energy_biomass,
            energyCharcoal: facilityData.energy_charcoal,
            energyAnimalWaste: facilityData.energy_animal_waste,
            energyElectricity: facilityData.energy_electricity,
            energyOther: facilityData.energy_other,
            energyCoalEnabled:
                facilityData.energy_coal_enabled ??
                !isEmpty(facilityData.energy_coal),
            energyNaturalGasEnabled:
                facilityData.energy_natural_gas_enabled ??
                !isEmpty(facilityData.energy_natural_gas),
            energyDieselEnabled:
                facilityData.energy_diesel_enabled ??
                !isEmpty(facilityData.energy_diesel),
            energyKeroseneEnabled:
                facilityData.energy_kerosene_enabled ??
                !isEmpty(facilityData.energy_kerosene),
            energyBiomassEnabled:
                facilityData.energy_biomass_enabled ??
                !isEmpty(facilityData.energy_biomass),
            energyCharcoalEnabled:
                facilityData.energy_charcoal_enabled ??
                !isEmpty(facilityData.energy_charcoal),
            energyAnimalWasteEnabled:
                facilityData.energy_animal_waste_enabled ??
                !isEmpty(facilityData.energy_animal_waste),
            energyElectricityEnabled:
                facilityData.energy_electricity_enabled ??
                !isEmpty(facilityData.energy_electricity),
            energyOtherEnabled:
                facilityData.energy_other_enabled ??
                !isEmpty(facilityData.energy_other),
        }),
        [facilityData],
    );

    const emissionsValidationErrors = useMemo(() => {
        try {
            freeEmissionsEstimateValidationSchema.validateSync(
                emissionsValidationValues,
                { abortEarly: false },
            );
            return {};
        } catch (validationError) {
            if (validationError?.inner?.length) {
                return validationError.inner.reduce((acc, err) => {
                    if (err.path) {
                        acc[err.path] = err.message;
                    }
                    return acc;
                }, {});
            }
            return {};
        }
    }, [emissionsValidationValues]);

    const hasEmissionsErrors = !isEmpty(emissionsValidationErrors);

    const getEmissionError = key => emissionsValidationErrors[key];

    const countryOptions = useMemo(
        () => createCountrySelectOptions(facilityData.countries || []),
        [facilityData.countries],
    );

    const sectorSelectOptions = useMemo(
        () => mapDjangoChoiceTuplesToSelectOptions(mockedSectors),
        [],
    );

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

    const energyFieldNameMap = {
        energyCoal: 'energy_coal',
        energyNaturalGas: 'energy_natural_gas',
        energyDiesel: 'energy_diesel',
        energyKerosene: 'energy_kerosene',
        energyBiomass: 'energy_biomass',
        energyCharcoal: 'energy_charcoal',
        energyAnimalWaste: 'energy_animal_waste',
        energyElectricity: 'energy_electricity',
        energyOther: 'energy_other',
    };

    const energyUpdaterMap = {
        energyCoal: updateEnergyCoal,
        energyNaturalGas: updateEnergyNaturalGas,
        energyDiesel: updateEnergyDiesel,
        energyKerosene: updateEnergyKerosene,
        energyBiomass: updateEnergyBiomass,
        energyCharcoal: updateEnergyCharcoal,
        energyAnimalWaste: updateEnergyAnimalWaste,
        energyElectricity: updateEnergyElectricity,
        energyOther: updateEnergyOther,
    };

    const energyEnabledKeyMap = {
        energyCoal: 'energy_coal_enabled',
        energyNaturalGas: 'energy_natural_gas_enabled',
        energyDiesel: 'energy_diesel_enabled',
        energyKerosene: 'energy_kerosene_enabled',
        energyBiomass: 'energy_biomass_enabled',
        energyCharcoal: 'energy_charcoal_enabled',
        energyAnimalWaste: 'energy_animal_waste_enabled',
        energyElectricity: 'energy_electricity_enabled',
        energyOther: 'energy_other_enabled',
    };

    const energyEnabledUpdaterMap = {
        energyCoal: updateEnergyCoalEnabled,
        energyNaturalGas: updateEnergyNaturalGasEnabled,
        energyDiesel: updateEnergyDieselEnabled,
        energyKerosene: updateEnergyKeroseneEnabled,
        energyBiomass: updateEnergyBiomassEnabled,
        energyCharcoal: updateEnergyCharcoalEnabled,
        energyAnimalWaste: updateEnergyAnimalWasteEnabled,
        energyElectricity: updateEnergyElectricityEnabled,
        energyOther: updateEnergyOtherEnabled,
    };

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
                            selectOptions={sectorSelectOptions}
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
                            hasValidationErrorFn={() =>
                                Boolean(
                                    getClaimedValidationError(
                                        'facility_website',
                                    ),
                                )
                            }
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
                        <InputSection
                            label="Parent Company / Supplier Group"
                            value={
                                get(data, 'facility_parent_company.name', '') ||
                                data.parent_company_name ||
                                ''
                            }
                            onChange={updateParentCompany}
                            disabled={updating}
                        />
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
                            error={Boolean(
                                getClaimedValidationError(
                                    'facility_workers_count',
                                ),
                            )}
                            helperText={
                                getClaimedValidationError(
                                    'facility_workers_count',
                                ) && (
                                    <InputErrorText
                                        text={getClaimedValidationError(
                                            'facility_workers_count',
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
                                    getClaimedValidationError(
                                        'facility_workers_count',
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
                            variant="headline"
                            className={classes.headingStyles}
                        >
                            Free Emissions Estimates
                        </Typography>
                        <Grid container spacing={24}>
                            <Grid item xs={12} md={6}>
                                <YearPicker
                                    value={data.opening_date || ''}
                                    label={openingDateField.label}
                                    tooltipText={openingDateField.tooltipText}
                                    placeholder={openingDateField.placeholder}
                                    helperText={
                                        getEmissionError('openingDate') && (
                                            <InputErrorText
                                                text={getEmissionError(
                                                    'openingDate',
                                                )}
                                            />
                                        )
                                    }
                                    disabled={updating}
                                    error={Boolean(
                                        getEmissionError('openingDate'),
                                    )}
                                    onChange={updateOpeningDate}
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <MonthYearPicker
                                    value={data.closing_date || ''}
                                    label={closingDateField.label}
                                    tooltipText={closingDateField.tooltipText}
                                    placeholderMonth={
                                        closingDateField.placeholderMonth
                                    }
                                    placeholderYear={
                                        closingDateField.placeholderYear
                                    }
                                    helperText={
                                        getEmissionError('closingDate') && (
                                            <InputErrorText
                                                text={getEmissionError(
                                                    'closingDate',
                                                )}
                                            />
                                        )
                                    }
                                    disabled={updating}
                                    error={Boolean(
                                        getEmissionError('closingDate'),
                                    )}
                                    onChange={updateClosingDate}
                                />
                            </Grid>
                        </Grid>
                        <div>
                            <InputSection
                                label={estimatedAnnualThroughputField.label}
                                value={data.estimated_annual_throughput || ''}
                                onChange={updateEstimatedAnnualThroughput}
                                disabled={updating}
                                hasValidationErrorFn={() =>
                                    Boolean(
                                        getEmissionError(
                                            'estimatedAnnualThroughput',
                                        ),
                                    )
                                }
                                FormHelperTextProps={{
                                    className: classes.helperText,
                                }}
                            />
                            {getEmissionError('estimatedAnnualThroughput') && (
                                <InputErrorText
                                    text={getEmissionError(
                                        'estimatedAnnualThroughput',
                                    )}
                                />
                            )}
                        </div>
                        <Typography
                            variant="title"
                            className={classes.paddedTitle}
                        >
                            {energyConsumptionLabel.label}
                        </Typography>
                        {energySourcesData.map(sourceData => {
                            const { valueFieldName, source } = sourceData;
                            const dataKey = energyFieldNameMap[valueFieldName];
                            const enabledKey =
                                energyEnabledKeyMap[valueFieldName];
                            const updater = energyUpdaterMap[valueFieldName];
                            const enabledUpdater =
                                energyEnabledUpdaterMap[valueFieldName];
                            const enabled =
                                data[enabledKey] ?? !isEmpty(data[dataKey]);
                            const errorText = getEmissionError(valueFieldName);
                            return (
                                <div key={valueFieldName}>
                                    <div
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '12px',
                                            flexWrap: 'wrap',
                                        }}
                                    >
                                        <div
                                            className={
                                                classes.switchSectionStyles
                                            }
                                            style={{
                                                alignItems: 'center',
                                                minWidth: 220,
                                                flexShrink: 0,
                                            }}
                                        >
                                            <Checkbox
                                                color="primary"
                                                onChange={event => {
                                                    const {
                                                        checked,
                                                    } = event.target;
                                                    enabledUpdater(event);
                                                    if (!checked) {
                                                        updater({
                                                            target: {
                                                                value: '',
                                                            },
                                                        });
                                                    }
                                                }}
                                                checked={enabled}
                                            />
                                            <Typography variant="body1">
                                                {`${source.label} (${source.unit})`}
                                            </Typography>
                                        </div>
                                        <div style={{ flex: 1, minWidth: 260 }}>
                                            <InputSection
                                                label={null}
                                                value={data[dataKey] || ''}
                                                onChange={updater}
                                                disabled={updating || !enabled}
                                                hasValidationErrorFn={() =>
                                                    enabled &&
                                                    Boolean(errorText)
                                                }
                                                FormHelperTextProps={{
                                                    className:
                                                        classes.helperText,
                                                }}
                                            />
                                        </div>
                                    </div>
                                    {enabled && errorText && (
                                        <InputErrorText text={errorText} />
                                    )}
                                </div>
                            );
                        })}
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
                            hasValidationErrorFn={() =>
                                Boolean(
                                    getClaimedValidationError(
                                        'point_of_contact_email',
                                    ),
                                )
                            }
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
                                    hasClaimedValidationErrors ||
                                    hasEmissionsErrors
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
    updateOpeningDate: func.isRequired,
    updateClosingDate: func.isRequired,
    updateEstimatedAnnualThroughput: func.isRequired,
    updateEnergyCoal: func.isRequired,
    updateEnergyNaturalGas: func.isRequired,
    updateEnergyDiesel: func.isRequired,
    updateEnergyKerosene: func.isRequired,
    updateEnergyBiomass: func.isRequired,
    updateEnergyCharcoal: func.isRequired,
    updateEnergyAnimalWaste: func.isRequired,
    updateEnergyElectricity: func.isRequired,
    updateEnergyOther: func.isRequired,
    updateEnergyCoalEnabled: func.isRequired,
    updateEnergyNaturalGasEnabled: func.isRequired,
    updateEnergyDieselEnabled: func.isRequired,
    updateEnergyKeroseneEnabled: func.isRequired,
    updateEnergyBiomassEnabled: func.isRequired,
    updateEnergyCharcoalEnabled: func.isRequired,
    updateEnergyAnimalWasteEnabled: func.isRequired,
    updateEnergyElectricityEnabled: func.isRequired,
    updateEnergyOtherEnabled: func.isRequired,
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
}) {
    return {
        user,
        fetching: fetchingData,
        data,
        errors: error || errorUpdating,
        updating,
        errorUpdating,
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
        updateParentCompany: makeDispatchValueFn(
            updateClaimedFacilityParentCompany,
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
        updateOpeningDate: value =>
            dispatch(updateClaimedFacilityOpeningDate(value)),
        updateClosingDate: value =>
            dispatch(updateClaimedFacilityClosingDate(value)),
        updateEstimatedAnnualThroughput: makeDispatchValueFn(
            updateClaimedEstimatedAnnualThroughput,
        ),
        updateEnergyCoal: makeDispatchValueFn(updateClaimedEnergyCoal),
        updateEnergyNaturalGas: makeDispatchValueFn(
            updateClaimedEnergyNaturalGas,
        ),
        updateEnergyDiesel: makeDispatchValueFn(updateClaimedEnergyDiesel),
        updateEnergyKerosene: makeDispatchValueFn(updateClaimedEnergyKerosene),
        updateEnergyBiomass: makeDispatchValueFn(updateClaimedEnergyBiomass),
        updateEnergyCharcoal: makeDispatchValueFn(updateClaimedEnergyCharcoal),
        updateEnergyAnimalWaste: makeDispatchValueFn(
            updateClaimedEnergyAnimalWaste,
        ),
        updateEnergyElectricity: makeDispatchValueFn(
            updateClaimedEnergyElectricity,
        ),
        updateEnergyOther: makeDispatchValueFn(updateClaimedEnergyOther),
        updateEnergyCoalEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyCoalEnabled,
        ),
        updateEnergyNaturalGasEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyNaturalGasEnabled,
        ),
        updateEnergyDieselEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyDieselEnabled,
        ),
        updateEnergyKeroseneEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyKeroseneEnabled,
        ),
        updateEnergyBiomassEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyBiomassEnabled,
        ),
        updateEnergyCharcoalEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyCharcoalEnabled,
        ),
        updateEnergyAnimalWasteEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyAnimalWasteEnabled,
        ),
        updateEnergyElectricityEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyElectricityEnabled,
        ),
        updateEnergyOtherEnabled: makeDispatchCheckedFn(
            updateClaimedEnergyOtherEnabled,
        ),
        submitUpdate: () =>
            dispatch(submitClaimedFacilityDetailsUpdate(claimID)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(mergedStyles)(ClaimedFacilitiesDetails));
