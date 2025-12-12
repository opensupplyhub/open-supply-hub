import { createReducer } from 'redux-act';
import update from 'immutability-helper';
import orderBy from 'lodash/orderBy';
import identity from 'lodash/identity';
import isString from 'lodash/isString';

import {
    startFetchClaimedFacilityDetails,
    failFetchClaimedFacilityDetails,
    completeFetchClaimedFacilityDetails,
    clearClaimedFacilityDetails,
    startUpdateClaimedFacilityDetails,
    failUpdateClaimedFacilityDetails,
    completeUpdateClaimedFacilityDetails,
    updateClaimedFacilityNameNativeLanguage,
    updateClaimedFacilityLocation,
    updateClaimedSector,
    updateClaimedFacilityPhone,
    updateClaimedFacilityPhoneVisibility,
    updateClaimedFacilityWebsite,
    updateClaimedFacilityWebsiteVisibility,
    updateClaimedFacilityDescription,
    updateClaimedFacilityMinimumOrder,
    updateClaimedFacilityAverageLeadTime,
    updateClaimedFacilityWorkersCount,
    updateClaimedFacilityFemaleWorkersPercentage,
    updateClaimedFacilityPointOfContactVisibility,
    updateClaimedFacilityContactPersonName,
    updateClaimedFacilityContactEmail,
    updateClaimedFacilityOfficeVisibility,
    updateClaimedFacilityOfficeName,
    updateClaimedFacilityOfficeAddress,
    updateClaimedFacilityOfficeCountry,
    updateClaimedFacilityOfficePhone,
    updateClaimedFacilityParentCompany,
    updateClaimedFacilityFacilityTypes,
    updateClaimedFacilityAffiliations,
    updateClaimedFacilityCertifications,
    updateClaimedFacilityProductTypes,
    updateClaimedFacilityProductionTypes,
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
} from '../actions/claimedFacilityDetails';

const initialState = Object.freeze({
    data: null,
    retrieveData: Object.freeze({
        fetching: false,
        error: null,
    }),
    updateData: Object.freeze({
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchClaimedFacilityDetails]: state =>
            update(state, {
                retrieveData: {
                    fetching: { $set: true },
                    error: { $set: initialState.retrieveData.error },
                },
                data: { $set: initialState.data },
            }),
        [failFetchClaimedFacilityDetails]: (state, error) =>
            update(state, {
                retrieveData: {
                    fetching: { $set: initialState.retrieveData.fetching },
                    error: { $set: error },
                },
            }),
        [completeFetchClaimedFacilityDetails]: (state, data) =>
            update(state, {
                retrieveData: {
                    $set: initialState.retrieveData,
                },
                data: {
                    $set: {
                        ...data,
                        initial_facility_address: data.facility_address,
                    },
                },
            }),
        [startUpdateClaimedFacilityDetails]: state =>
            update(state, {
                updateData: {
                    fetching: { $set: true },
                    error: { $set: initialState.updateData.error },
                },
            }),
        [failUpdateClaimedFacilityDetails]: (state, error) =>
            update(state, {
                updateData: {
                    fetching: { $set: initialState.updateData.fetching },
                    error: { $set: error },
                },
            }),
        [completeUpdateClaimedFacilityDetails]: (state, data) =>
            update(state, {
                updateData: {
                    $set: initialState.updateData,
                },
                data: {
                    $set: {
                        ...data,
                        initial_facility_address: data.facility_address,
                    },
                },
            }),
        [updateClaimedFacilityNameNativeLanguage]: (state, name) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_name_native_language: { $set: name },
                },
            }),
        [updateClaimedFacilityWorkersCount]: (state, workersCount) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_workers_count: { $set: workersCount },
                },
            }),
        [updateClaimedFacilityFemaleWorkersPercentage]: (state, percentage) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_female_workers_percentage: {
                        $set: percentage,
                    },
                },
            }),
        [updateClaimedFacilityAffiliations]: (state, affiliations) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_affiliations: {
                        $set: orderBy(affiliations, identity),
                    },
                },
            }),
        [updateClaimedFacilityCertifications]: (state, certifications) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_certifications: {
                        $set: orderBy(certifications, identity),
                    },
                },
            }),
        [updateClaimedFacilityProductTypes]: (state, productTypes) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_product_types: {
                        $set: orderBy(productTypes, identity),
                    },
                },
            }),
        [updateClaimedFacilityProductionTypes]: (state, productionTypes) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_production_types: {
                        $set: orderBy(productionTypes, identity),
                    },
                },
            }),
        [updateClaimedFacilityLocation]: (state, location) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_location: { $set: location },
                },
            }),
        [updateClaimedSector]: (state, sectors) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    sector: {
                        $set: orderBy(sectors, identity),
                    },
                },
            }),
        [updateClaimedFacilityPhone]: (state, phone) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_phone_number: { $set: phone },
                },
            }),
        [updateClaimedFacilityPhoneVisibility]: (state, visible) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_phone_number_publicly_visible: { $set: visible },
                },
            }),
        [updateClaimedFacilityParentCompany]: (state, parentCompany) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_parent_company: {
                        $set: isString(parentCompany)
                            ? { id: null, name: parentCompany }
                            : parentCompany,
                    },
                    parent_company_name: {
                        $set: isString(parentCompany)
                            ? parentCompany
                            : parentCompany?.name || '',
                    },
                },
            }),
        [updateClaimedFacilityPointOfContactVisibility]: (state, visible) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    point_of_contact_publicly_visible: { $set: visible },
                },
            }),
        [updateClaimedFacilityOfficeVisibility]: (state, visible) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    office_info_publicly_visible: { $set: visible },
                },
            }),
        [updateClaimedFacilityWebsite]: (state, website) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_website: { $set: website },
                },
            }),
        [updateClaimedFacilityWebsiteVisibility]: (state, visible) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_website_publicly_visible: { $set: visible },
                },
            }),
        [updateClaimedFacilityDescription]: (state, description) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_description: { $set: description },
                },
            }),
        [updateClaimedFacilityMinimumOrder]: (state, minOrder) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_minimum_order_quantity: { $set: minOrder },
                },
            }),
        [updateClaimedFacilityAverageLeadTime]: (state, avgLeadTime) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_average_lead_time: { $set: avgLeadTime },
                },
            }),
        [updateClaimedFacilityFacilityTypes]: (state, type) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    facility_type: { $set: type },
                },
            }),
        [updateClaimedFacilityContactPersonName]: (state, person) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    point_of_contact_person_name: { $set: person },
                },
            }),
        [updateClaimedFacilityContactEmail]: (state, email) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    point_of_contact_email: { $set: email },
                },
            }),
        [updateClaimedFacilityOfficeName]: (state, name) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    office_official_name: { $set: name },
                },
            }),
        [updateClaimedFacilityOfficeAddress]: (state, address) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    office_address: { $set: address },
                },
            }),
        [updateClaimedFacilityOfficeCountry]: (state, country) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    office_country_code: { $set: country },
                },
            }),
        [updateClaimedFacilityOfficePhone]: (state, phone) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    office_phone_number: { $set: phone },
                },
            }),
        [updateClaimedFacilityOpeningDate]: (state, openingDate) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    opening_date: { $set: openingDate },
                },
            }),
        [updateClaimedFacilityClosingDate]: (state, closingDate) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    closing_date: { $set: closingDate },
                },
            }),
        [updateClaimedEstimatedAnnualThroughput]: (state, throughput) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    estimated_annual_throughput: { $set: throughput },
                },
            }),
        [updateClaimedEnergyCoal]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_coal: { $set: value },
                },
            }),
        [updateClaimedEnergyNaturalGas]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_natural_gas: { $set: value },
                },
            }),
        [updateClaimedEnergyDiesel]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_diesel: { $set: value },
                },
            }),
        [updateClaimedEnergyKerosene]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_kerosene: { $set: value },
                },
            }),
        [updateClaimedEnergyBiomass]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_biomass: { $set: value },
                },
            }),
        [updateClaimedEnergyCharcoal]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_charcoal: { $set: value },
                },
            }),
        [updateClaimedEnergyAnimalWaste]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_animal_waste: { $set: value },
                },
            }),
        [updateClaimedEnergyElectricity]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_electricity: { $set: value },
                },
            }),
        [updateClaimedEnergyOther]: (state, value) =>
            update(state, {
                updateData: {
                    error: { $set: initialState.updateData.error },
                },
                data: {
                    energy_other: { $set: value },
                },
            }),
        [clearClaimedFacilityDetails]: () => initialState,
    },
    initialState,
);
