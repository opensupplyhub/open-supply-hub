import { createAction } from 'redux-act';
import mapValues from 'lodash/mapValues';
import trim from 'lodash/trim';
import isNull from 'lodash/isNull';
import omit from 'lodash/omit';
import isInteger from 'lodash/isInteger';
import toString from 'lodash/toString';
import get from 'lodash/get';
import { isInt } from 'validator';
import map from 'lodash/map';

import apiRequest from '../util/apiRequest';

import {
    logErrorAndDispatchFailure,
    makeGetOrUpdateApprovedFacilityClaimURL,
} from '../util/util';

export const startFetchClaimedFacilityDetails = createAction(
    'START_FETCH_CLAIMED_FACILITY_DETAILS',
);
export const failFetchClaimedFacilityDetails = createAction(
    'FAIL_FETCH_CLAIMED_FACILITY_DETAILS',
);
export const completeFetchClaimedFacilityDetails = createAction(
    'COMPLETE_FETCH_CLAIMED_FACILITY_DETAILS',
);
export const clearClaimedFacilityDetails = createAction(
    'CLEAR_CLAIMED_FACILITY_DETAILS',
);

export function fetchClaimedFacilityDetails(claimID) {
    return dispatch => {
        if (!claimID) {
            return null;
        }

        dispatch(startFetchClaimedFacilityDetails());

        return apiRequest
            .get(makeGetOrUpdateApprovedFacilityClaimURL(claimID))
            .then(({ data }) =>
                mapValues(data, v => {
                    if (isNull(v)) {
                        return '';
                    }

                    return v;
                }),
            )
            .then(data => dispatch(completeFetchClaimedFacilityDetails(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching details about that claimed facility',
                        failFetchClaimedFacilityDetails,
                    ),
                ),
            );
    };
}

export const startUpdateClaimedFacilityDetails = createAction(
    'START_UPDATE_CLAIMED_FACILITY_DETAILS',
);
export const failUpdateClaimedFacilityDetails = createAction(
    'FAIL_UPDATE_CLAIMED_FACILITY_DETAILS',
);
export const completeUpdateClaimedFacilityDetails = createAction(
    'COMPLETE_UPDATE_CLAIMED_FACILITY_DETAILS',
);

export const updateClaimedEnergyCoalEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_COAL_ENABLED',
);
export const updateClaimedEnergyNaturalGasEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_NATURAL_GAS_ENABLED',
);
export const updateClaimedEnergyDieselEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_DIESEL_ENABLED',
);
export const updateClaimedEnergyKeroseneEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_KEROSENE_ENABLED',
);
export const updateClaimedEnergyBiomassEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_BIOMASS_ENABLED',
);
export const updateClaimedEnergyCharcoalEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_CHARCOAL_ENABLED',
);
export const updateClaimedEnergyAnimalWasteEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_ANIMAL_WASTE_ENABLED',
);
export const updateClaimedEnergyElectricityEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_ELECTRICITY_ENABLED',
);
export const updateClaimedEnergyOtherEnabled = createAction(
    'UPDATE_CLAIMED_ENERGY_OTHER_ENABLED',
);

export function submitClaimedFacilityDetailsUpdate(claimID) {
    return (dispatch, getState) => {
        const {
            claimedFacilityDetails: { data },
        } = getState();

        if (!data || !claimID) {
            return null;
        }

        dispatch(startUpdateClaimedFacilityDetails());

        const parentCompanyName = (() => {
            const name =
                data.parent_company_name ||
                get(data, 'facility_parent_company.name', '');
            const trimmedName = trim(toString(name));

            return trimmedName === '' ? null : trimmedName;
        })();

        const energyFields = [
            'energy_coal',
            'energy_natural_gas',
            'energy_diesel',
            'energy_kerosene',
            'energy_biomass',
            'energy_charcoal',
            'energy_animal_waste',
            'energy_electricity',
            'energy_other',
        ];
        const energyEnabledKeys = map(
            energyFields,
            fieldName => `${fieldName}_enabled`,
        );

        const updateData = Object.assign(
            {},
            omit(data, [
                'contributors',
                'countries',
                'facility_types',
                'affiliation_choices',
                'certification_choices',
                'production_type_choices',
                'initial_facility_address',
                ...energyEnabledKeys,
            ]),
            {
                facility_workers_count: data.facility_workers_count,
                facility_female_workers_percentage:
                    isInteger(data.facility_female_workers_percentage) ||
                    isInt(data.facility_female_workers_percentage)
                        ? data.facility_female_workers_percentage
                        : null,
                parent_company_name: parentCompanyName,
                opening_date: data.opening_date || null,
                closing_date: data.closing_date || null,
                estimated_annual_throughput:
                    data.estimated_annual_throughput || null,
            },
        );

        // Only include energy fields if the corresponding checkbox is enabled.
        energyFields.forEach(fieldName => {
            const enabledKey = `${fieldName}_enabled`;
            if (data[enabledKey]) {
                updateData[fieldName] = data[fieldName] || null;
            }
        });

        return apiRequest
            .put(makeGetOrUpdateApprovedFacilityClaimURL(claimID), updateData)
            .then(({ data: responseData }) =>
                mapValues(responseData, v => {
                    if (isNull(v)) {
                        return '';
                    }

                    return v;
                }),
            )
            .then(responseData =>
                dispatch(completeUpdateClaimedFacilityDetails(responseData)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        "An error prevented updating that facility claim's details",
                        failUpdateClaimedFacilityDetails,
                    ),
                ),
            );
    };
}

export const updateClaimedFacilityNameNativeLanguage = createAction(
    'UPDATE_CLAIMED_FACILITY_NAME_NATIVE_LANGUAGE',
);
export const updateClaimedSector = createAction('UPDATE_CLAIMED_SECTOR');
export const updateClaimedFacilityPhone = createAction(
    'UPDATE_CLAIMED_FACILITY_PHONE',
);
export const updateClaimedFacilityPhoneVisibility = createAction(
    'UPDATE_CLAIMED_FACILITY_PHONE_VISIBILITY',
);
export const updateClaimedFacilityWebsite = createAction(
    'UPDATE_CLAIMED_FACILITY_WEBSITE',
);
export const updateClaimedFacilityWebsiteVisibility = createAction(
    'UPDATE_CLAIMED_FACILITY_WEBSITE_VISIBILITY',
);
export const updateClaimedFacilityDescription = createAction(
    'UPDATE_CLAIMED_FACILITY_DESCRIPTION',
);
export const updateClaimedFacilityMinimumOrder = createAction(
    'UPDATE_CLAIMED_FACILITY_MINIMUM_ORDER',
);
export const updateClaimedFacilityAverageLeadTime = createAction(
    'UPDATE_CLAIMED_FACILITY_AVERAGE_LEAD_TIME',
);
export const updateClaimedFacilityWorkersCount = createAction(
    'UPDATE_CLAIMED_FACILITY_WORKERS_COUNT',
);
export const updateClaimedFacilityFemaleWorkersPercentage = createAction(
    'UPDATE_CLAIMED_FACILITY_FEMALE_WORKERS_PERCENTAGE',
);
export const updateClaimedFacilityPointOfContactVisibility = createAction(
    'UPDATE_CLAIMED_FACILITY_POINT_OF_CONTACT_VISIBILITY',
);
export const updateClaimedFacilityContactPersonName = createAction(
    'UPDATE_CLAIMED_FACILITY_CONTACT_PERSON_NAME',
);
export const updateClaimedFacilityContactEmail = createAction(
    'UPDATE_CLAIMED_FACILITY_CONTACT_EMAIL',
);
export const updateClaimedFacilityOfficeVisibility = createAction(
    'UPDATE_CLAIMED_FACILITY_OFFICE_VISIBILITY',
);
export const updateClaimedFacilityOfficeName = createAction(
    'UPDATE_CLAIMED_FACILITY_OFFICE_NAME',
);
export const updateClaimedFacilityOfficeAddress = createAction(
    'UPDATE_CLAIMED_FACILITY_OFFICE_ADDRESS',
);
export const updateClaimedFacilityOfficeCountry = createAction(
    'UPDATE_CLAIMED_FACILITY_OFFICE_COUNTRY',
);
export const updateClaimedFacilityOfficePhone = createAction(
    'UPDATE_CLAIMED_FACILITY_OFFICE_PHONE',
);
export const updateClaimedFacilityParentCompany = createAction(
    'UPDATE_CLAIMED_FACILITY_PARENT_COMPANY',
);
export const updateClaimedFacilityFacilityTypes = createAction(
    'UPDATE_CLAIMED_FACILITY_FACILITY_TYPES',
);
export const updateClaimedFacilityAffiliations = createAction(
    'UPDATE_CLAIMED_FACILITY_AFFILIATIONS',
);
export const updateClaimedFacilityCertifications = createAction(
    'UPDATE_CLAIMED_FACILITY_CERTIFICATIONS',
);
export const updateClaimedFacilityProductTypes = createAction(
    'UPDATE_CLAIMED_FACILITY_PRODUCT_TYPES',
);
export const updateClaimedFacilityProductionTypes = createAction(
    'UPDATE_CLAIMED_FACILITY_PRODUCTION_TYPES',
);

export const updateClaimedFacilityLocation = createAction(
    'UPDATE_CLAIMED_FACILITY_LOCATION',
);

export const updateClaimedFacilityOpeningDate = createAction(
    'UPDATE_CLAIMED_FACILITY_OPENING_DATE',
);
export const updateClaimedFacilityClosingDate = createAction(
    'UPDATE_CLAIMED_FACILITY_CLOSING_DATE',
);
export const updateClaimedEstimatedAnnualThroughput = createAction(
    'UPDATE_CLAIMED_ESTIMATED_ANNUAL_THROUGHPUT',
);
export const updateClaimedEnergyCoal = createAction(
    'UPDATE_CLAIMED_ENERGY_COAL',
);
export const updateClaimedEnergyNaturalGas = createAction(
    'UPDATE_CLAIMED_ENERGY_NATURAL_GAS',
);
export const updateClaimedEnergyDiesel = createAction(
    'UPDATE_CLAIMED_ENERGY_DIESEL',
);
export const updateClaimedEnergyKerosene = createAction(
    'UPDATE_CLAIMED_ENERGY_KEROSENE',
);
export const updateClaimedEnergyBiomass = createAction(
    'UPDATE_CLAIMED_ENERGY_BIOMASS',
);
export const updateClaimedEnergyCharcoal = createAction(
    'UPDATE_CLAIMED_ENERGY_CHARCOAL',
);
export const updateClaimedEnergyAnimalWaste = createAction(
    'UPDATE_CLAIMED_ENERGY_ANIMAL_WASTE',
);
export const updateClaimedEnergyElectricity = createAction(
    'UPDATE_CLAIMED_ENERGY_ELECTRICITY',
);
export const updateClaimedEnergyOther = createAction(
    'UPDATE_CLAIMED_ENERGY_OTHER',
);
