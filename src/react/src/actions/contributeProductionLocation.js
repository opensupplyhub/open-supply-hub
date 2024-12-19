import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    makeGetProductionLocationByOsIdURL,
} from '../util/util';

export const startFetchSingleProductionLocation = createAction(
    'START_FETCH_SINGLE_PRODUCTION_LOCATION',
);
export const failFetchSingleProductionLocation = createAction(
    'FAIL_FETCH_SINGLE_PRODUCTION_LOCATION',
);
export const completeFetchSingleProductionLocation = createAction(
    'COMPLETE_FETCH_SINGLE_PRODUCTION_LOCATION',
);
export const resetSingleProductionLocation = createAction(
    'RESET_SINGLE_PRODUCTION_LOCATION',
);
export const startFetchProductionLocations = createAction(
    'START_FETCH_PRODUCTION_LOCATIONS',
);
export const failFetchProductionLocations = createAction(
    'FAIL_FETCH_PRODUCTION_LOCATIONS',
);
export const completeFetchProductionLocations = createAction(
    'COMPLETE_FETCH_PRODUCTION_LOCATIONS',
);

export function fetchProductionLocationByOsId(osID) {
    return dispatch => {
        dispatch(startFetchSingleProductionLocation());

        return apiRequest
            .get(makeGetProductionLocationByOsIdURL(osID))
            .then(({ data }) =>
                dispatch(completeFetchSingleProductionLocation(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching data about that production location',
                        failFetchSingleProductionLocation,
                    ),
                ),
            );
    };
}

const mockedProductionLocations = [
    {
        sector: ['Apparel'],
        location_type: ['Contractor', 'Logo Application'],
        name: 'Robinson Manufacturing Company Dayton',
        parent_company: 'Robinson',
        claim_status: 'unclaimed',
        number_of_workers: {
            max: 53,
            min: 53,
        },
        product_type: ['Accessories', 'Decoration'],
        coordinates: {
            lat: 35.4872298,
            lng: -85.0189463,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '798 Market Street, Dayton, Dayton, Tennessee 37321',
        os_id: 'US2019085AACCK0',
        processing_type: ['Contractor', 'Logo Application'],
    },
    {
        sector: ['Apparel'],
        location_type: ['Finished Goods'],
        name: 'Robinson Manufacturing Company, Dayton',
        parent_company: 'ROBINSON',
        claim_status: 'unclaimed',
        number_of_workers: {
            max: 58,
            min: 58,
        },
        product_type: ['APPAREL', 'NIKE'],
        coordinates: {
            lat: 35.5118656,
            lng: -85.0064775,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '1184 Broadway Dayton Tennessee 37321',
        os_id: 'US2022082XJ6DVN',
        processing_type: ['Finished Goods'],
    },
    {
        sector: ['Consumer Products', 'General Merchandise'],
        location_type: ['Manufacturing', 'Production', 'Logo Application'],
        name: 'Robinson Manufacturing',
        claim_status: 'unclaimed',
        product_type: ['Accessories', 'Loungewear', 'Sleepwear', 'Underwear'],
        coordinates: {
            lat: 35.4872298,
            lng: -85.0189463,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address:
            '798 S. Market Street, Dayton, Tennessee, 37321, United States',
        os_id: 'US2024275MWQQ62',
        processing_type: ['Manufacturing', 'Production', 'Logo Application'],
    },
    {
        sector: ['Agriculture', 'Farming'],
        name: 'GRUBER MANUFACTURING, INC',
        claim_status: 'unclaimed',
        coordinates: {
            lat: 39.6900755,
            lng: -121.8560144,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '2462 Dayton Road, CHICO, CA, 95928-8225',
        os_id: 'US2024299KEN8HK',
    },
    {
        sector: ['Chemicals', 'Commodities', 'Waste Management'],
        location_type: [
            'Onsite Chemical Disposal',
            'Offsite Chemical Disposal',
        ],
        name: 'CPCA MANUFACTURING LLC',
        claim_status: 'unclaimed',
        coordinates: {
            lat: 39.762,
            lng: -84.227,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '750 ROSEDALE DR, DAYTON OHIO 45402 (MONTGOMERY)',
        os_id: 'US2024212DV02QP',
        processing_type: [
            'Onsite Chemical Disposal',
            'Offsite Chemical Disposal',
        ],
    },
    {
        sector: ['Apparel', 'Apparel Accessories'],
        name: 'E T Manufacturing & Sales, Inc.',
        claim_status: 'unclaimed',
        coordinates: {
            lat: 40.8727141,
            lng: -74.1177198,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '90 Dayton Ave, Passaic, NJ, 07055',
        os_id: 'US2024275HE0B6E',
    },
    {
        sector: ['Chemicals', 'Commodities', 'Waste Management'],
        location_type: [
            'Offsite Chemical Disposal',
            'Onsite Chemical Disposal',
        ],
        name: 'HOHMAN PLATING & MANUFACTURING INC',
        claim_status: 'unclaimed',
        coordinates: {
            lat: 39.784,
            lng: -84.185,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '814 HILLROSE AVE, DAYTON OHIO 45404 (MONTGOMERY)',
        os_id: 'US2024212GE5H1A',
        processing_type: [
            'Offsite Chemical Disposal',
            'Onsite Chemical Disposal',
        ],
    },
    {
        sector: ['Health', 'Medical Equipment & Services'],
        name: 'GEM City Enginnering and Manufacturing Corporation',
        claim_status: 'unclaimed',
        coordinates: {
            lat: 39.7842949,
            lng: -84.1911605,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '401 Leo St Dayton, Ohio 45404',
        os_id: 'US2024283CJQHGK',
    },
    {
        sector: ['Chemicals', 'Commodities', 'Waste Management'],
        location_type: [
            'Onsite Chemical Disposal',
            'Offsite Chemical Disposal',
        ],
        name: 'MAYDAY MANUFACTURING CO',
        claim_status: 'unclaimed',
        coordinates: {
            lat: 33.22,
            lng: -97.174,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '3100 JIM CHRISTAL RD, DENTON TEXAS 76207 (DENTON)',
        os_id: 'US2024213ZB3ZHK',
        processing_type: [
            'Onsite Chemical Disposal',
            'Offsite Chemical Disposal',
        ],
    },
    {
        sector: ['Health', 'Healthcare', 'Pharmaceuticals'],
        name: 'Kobayashi America Manufacturing, LLC',
        parent_company: 'Kobayashi Consumer Products LLC',
        claim_status: 'unclaimed',
        coordinates: {
            lat: 34.7045473,
            lng: -84.9496968,
        },
        country: {
            name: 'United States',
            numeric: '840',
            alpha_3: 'USA',
            alpha_2: 'US',
        },
        address: '245 Kraft Dr Dalton, Georgia 30721',
        os_id: 'US2023084VCWT7Z',
    },
];

export function fetchProductionLocations() {
    return async dispatch => {
        dispatch(startFetchProductionLocations());

        // TODO: Replace the mock implementation with an actual API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1175
        return new Promise(resolve => {
            setTimeout(
                () => resolve({ data: mockedProductionLocations }),
                1000,
            );
        })
            .then(({ data }) =>
                dispatch(completeFetchProductionLocations(data)),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching production locations',
                        failFetchProductionLocations,
                    ),
                ),
            );
    };
}
