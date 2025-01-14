/* eslint no-unused-vars: 0 */
import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';
import {
    logErrorAndDispatchFailure,
    makeGetProductionLocationURL,
    generateRangeField,
    extractProductionLocationContributionValues,
} from '../util/util';

import { DATA_SOURCES_ENUM } from '../util/constants';

// This action is needed to fetch existing production location by OS ID
// It is using in src/react/src/components/Contribute/SearchByOsIdResult.jsx
// but response data is not rendered because 5 and 5b screens in progress.
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
export const resetProductionLocations = createAction(
    'RESET_PRODUCTION_LOCATIONS',
);

// TODO: This actions should use 'src/react/src/reducers/DashboardContributionRecordReducer.js' from OSDEV-1117
// Regular contributor can get moderation event
// OS ID will be rendered depending on request_type and os_id presence. But only moderator can change it's status
export const startCreateProductionLocation = createAction(
    'START_CREATE_PRODUCTION_LOCATION',
);

export const completeCreateProductionLocation = createAction(
    'COMPLETE_CREATE_PRODUCTION_LOCATION',
);

export const failCreateProductionLocation = createAction(
    'FAIL_CREATE_PRODUCTION_LOCATION',
);

export const startUpdateProductionLocation = createAction(
    'START_UPDATE_PRODUCTION_LOCATION',
);

export const completeUpdateProductionLocation = createAction(
    'COMPLETE_UPDATE_PRODUCTION_LOCATION',
);

export const failUpdateProductionLocation = createAction(
    'FAIL_UPDATE_PRODUCTION_LOCATION',
);

export function createProductionLocation(contribData) {
    const {
        name,
        address,
        country,
        sector,
        productType,
        locationType,
        processingType,
        numberOfWorkers,
        parentCompany,
    } = contribData;

    const parsedContribData = {
        source: DATA_SOURCES_ENUM.SLC,
        name,
        address,
        country: country.value,
        sector: extractProductionLocationContributionValues(sector),
        parent_company: extractProductionLocationContributionValues(
            parentCompany,
        ),
        product_type: extractProductionLocationContributionValues(productType),
        location_type: extractProductionLocationContributionValues(
            locationType,
        ),
        processing_type: extractProductionLocationContributionValues(
            processingType,
        ),
        // TODO: refactor later
        number_of_workers: generateRangeField(numberOfWorkers),
    };

    return async dispatch => {
        dispatch(startCreateProductionLocation());

        try {
            const { data } = await apiRequest.post(
                makeGetProductionLocationURL(),
                parsedContribData,
            );
            return dispatch(completeCreateProductionLocation(data));
        } catch (err) {
            return dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented creating production location',
                    failCreateProductionLocation,
                ),
            );
        }
    };
}

export function updateProductionLocation(osID) {
    return async dispatch => {
        dispatch(startUpdateProductionLocation());

        try {
            const { data } = await apiRequest.update(
                makeGetProductionLocationURL(osID),
            );
            return dispatch(completeUpdateProductionLocation(data));
        } catch (err) {
            return dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented creating production location',
                    failUpdateProductionLocation,
                ),
            );
        }
    };
}

// TODO: Remove mockedProductionLocations after implementation of an actual
// API call as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1374
const mockedProductionLocations = {
    count: 50,
    data: [
        {
            sector: ['Apparel'],
            location_type: ['Contractor', 'Logo Application'],
            name: 'Robinson Manufacturing Company Dayton Very Long Name',
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
            product_type: [
                'Accessories',
                'Loungewear',
                'Sleepwear',
                'Underwear',
            ],
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
            processing_type: [
                'Manufacturing',
                'Production',
                'Logo Application',
            ],
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
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            name:
                'GLOBAL TUBING LLC COILED TUBING MANUFACTURING FACILITY IN DA',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 30.023,
                lng: -94.904,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '501 CR 493, DAYTON TEXAS 77535 (LIBERTY)',
            os_id: 'US2024213M0RG2M',
        },
        {
            sector: ['Manufacturing'],
            name: 'CF MANUFACTURING LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 29.1883701,
                lng: -81.0338419,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '828 S nova rd, daytona beach, FL, 32114-5802',
            os_id: 'US2024294RSD344',
        },
        {
            sector: ['Manufacturing'],
            name: 'RUT MANUFACTURING, INC.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.5659544,
                lng: -80.09753839999999,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '22650 HWY 109, DENTON, NC 27239',
            os_id: 'US2024302BWQVJ0',
        },
        {
            sector: ['Waste Management'],
            location_type: ['RCRAInfo subtitle C (Hazardous waste handlers)'],
            name: 'ALADDIN MANUFACTURING CORP - MCFARLAND RD',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 34.72919,
                lng: -84.96658,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '104 MCFARLAND RD, DALTON, GA, 30721',
            os_id: 'US202427424D36S',
            processing_type: ['RCRAInfo subtitle C (Hazardous waste handlers)'],
        },
        {
            sector: ['Health', 'Medical Equipment & Services'],
            name: 'Product Quest Manufacturing LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 29.2313552,
                lng: -81.03630100000001,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '330 Carswell Ave Daytona Beach, Florida 32117',
            os_id: 'US2024284HFGCME',
        },
        {
            sector: ['Apparel'],
            location_type: ['Logo Application', 'Contractor'],
            name: 'CROWN MANUFACTURING',
            historical_os_id: ['US20190853PWY1N', 'US20203490X4Q5S'],
            claim_status: 'unclaimed',
            number_of_workers: {
                max: 71,
                min: 71,
            },
            coordinates: {
                lat: 35.2102754,
                lng: -89.7832442,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '8390 WOLF LAKE DRIVE BARTLETT TENNESSEE 38133',
            os_id: 'US20242498JW7NH',
            processing_type: ['Logo Application', 'Contractor'],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'BTD MANUFACTURING INC.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 34.359,
                lng: -84.051,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '55 IMPULSE DR, DAWSONVILLE GEORGIA 30534 (DAWSON)',
            os_id: 'US2024213RVKAGP',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'SCHAEFFER MANUFACTURING',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 38.6,
                lng: -90.199,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '102 BARTON ST, SAINT LOUIS MISSOURI 63104 (ST LOUIS (CITY))',
            os_id: 'US20242120TZ4P8',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Food'],
            name: 'Buchanan Manufacturing, Inc.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 36.382747,
                lng: -88.222516,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '575 Cowpath Rd Buchanan, Tennessee 38222',
            os_id: 'US2024284RA1K9X',
        },
        {
            sector: ['Metal Manufacturing'],
            name: 'APEX MANUFACTURING GROUP INC.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 39.6522694,
                lng: -75.7258085,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '825 Dawson Drive Ste 1, Newark, DE, 19713',
            os_id: 'US2024292N604QK',
        },
        {
            sector: ['Equipment', 'Manufacturing'],
            name: 'JACKSON CREEK MANUFACTURING INC.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.6187618,
                lng: -80.08854439999999,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '206 Bingham Industrial Dr., DENTON, NC 27239-7795',
            os_id: 'US2024302F2292K',
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            name: 'ORTHMAN MANUFACTURING INC NORTH PLANT',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 40.81,
                lng: -99.711,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '75765 RD 435, LEXINGTON NEBRASKA 68850 (DAWSON)',
            os_id: 'US2024213T818RS',
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'CLOROX PRODUCTS MANUFACTURING',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 33.627,
                lng: -84.391,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '115 LAKE MIRROR RD, FOREST PARK GEORGIA 30297 (CLAYTON)',
            os_id: 'US20242132MFEPZ',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Apparel'],
            name: 'Wise Manufacturing, Inc',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 36.2646365,
                lng: -86.67173249999999,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '645 Old Hickory Blvd. Nashville Tennessee 37138',
            os_id: 'US2020254R737MM',
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'SCHICK MANUFACTURING INC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.959,
                lng: -83.828,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '2820 MEDIA DR, KNOXVILLE TENNESSEE 37914 (KNOX)',
            os_id: 'US202421339SE09',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Offsite Chemical Disposal',
                'Onsite Chemical Disposal',
            ],
            name: 'BATESVILLE MANUFACTURING LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.498,
                lng: -86.072,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '175 MONOGARD DR, MANCHESTER TENNESSEE 37355 (COFFEE)',
            os_id: 'US20242127SXDVT',
            processing_type: [
                'Offsite Chemical Disposal',
                'Onsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'MODINE MANUFACTURING CO',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.266,
                lng: -87.329,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '2009 REMKE AVE, LAWRENCEBURG TENNESSEE 38464 (LAWRENCE)',
            os_id: 'US2024213H2KNN6',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Offsite Chemical Disposal',
                'Onsite Chemical Disposal',
            ],
            name: 'TAG MANUFACTURING INC.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.076,
                lng: -85.15,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '6989 DISCOVERY DR., CHATTANOOGA TENNESSEE 37416 (HAMILTON)',
            os_id: 'US20242136X89CP',
            processing_type: [
                'Offsite Chemical Disposal',
                'Onsite Chemical Disposal',
            ],
        },
        {
            sector: ['Health', 'Healthcare', 'Pharmaceuticals'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'Iatric Manufacturing Solutions, LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 36.2425997,
                lng: -83.21361069999999,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '328 Hamblen Ave Morristown, Tennessee 37813',
            os_id: 'US2024213TGT532',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Food'],
            location_type: ['Confectionery Merchant Wholesalers'],
            name: 'Wrigley Manufacturing Company, LLC',
            claim_status: 'unclaimed',
            product_type: ['Confectionery'],
            coordinates: {
                lat: 35.0575,
                lng: -85.19637700000001,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '3002 Jersey Pike Chattanooga, Tennessee 37421',
            os_id: 'US202424494DHFM',
            processing_type: ['Confectionery Merchant Wholesalers'],
        },
        {
            sector: ['Health', 'Medical Equipment & Services'],
            name: 'Valley Manufacturing Co Inc',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.8973921,
                lng: -86.8720665,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '104 Beta Dr Franklin, Tennessee 37064',
            os_id: 'US2024286AFYPT7',
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'PIOLAX MANUFACTURING PLANT EXPANSION',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 34.247,
                lng: -84.472,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '140 ETOWAH INDUSTRIAL CT, CANTON GEORGIA 30114 (CHEROKEE)',
            os_id: 'US2024212BWK8E5',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'POLARTEC TENNESSEE MANUFACTURING',
            parent_company: 'Polartec, LLC',
            claim_status: 'unclaimed',
            product_type: ['Materials Manufacturing'],
            coordinates: {
                lat: 35.133,
                lng: -84.903,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '310 INDUSTRIAL DR SW, CLEVELAND TENNESSEE 37311 (BRADLEY)',
            os_id: 'US2019083XFE7PP',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'LODGE MANUFACTURING CO',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.008,
                lng: -85.706,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '600 RAILROAD AVENUE, SOUTH PITTSBURG TENNESSEE 37380 (MARION)',
            os_id: 'US20242135BDJ49',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'RAVAGO MANUFACTURING AMERICAS',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.437,
                lng: -86.025,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '405 PARK TOWER DR, MANCHESTER TENNESSEE 37355 (COFFEE)',
            os_id: 'US2024213QKT0VN',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Offsite Chemical Disposal',
                'Onsite Chemical Disposal',
            ],
            name: 'IBC MANUFACTURING CO',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.063,
                lng: -90.078,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '416 E BROOKS RD, MEMPHIS TENNESSEE 38109 (SHELBY)',
            os_id: 'US20242136SY670',
            processing_type: [
                'Offsite Chemical Disposal',
                'Onsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            name: 'MANUFACTURING SCIENCES CORP',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 36.004,
                lng: -84.232,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '804 S ILLINOIS AVE, OAK RIDGE TENNESSEE 37830 (ANDERSON)',
            os_id: 'US20242131D840G',
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'OSHKOSH MANUFACTURING LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 36.107,
                lng: -83.495,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '1400 FLAT GAP RD, JEFFERSON CITY TENNESSEE 37760 (JEFFERSON)',
            os_id: 'US2024213ES9NJD',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'WABTEC MANUFACTURING SOLUTIONS LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 33.029,
                lng: -97.302,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '16201 THREE WIDE DR, FORT WORTH TEXAS 76177 (DENTON)',
            os_id: 'US202421385TFP2',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Food'],
            name: 'Memphis Pyramid Barbecue Sauce Manufacturing Co',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.0575559,
                lng: -89.3036889,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '19600 Highway 57 Moscow, Tennessee 38057',
            os_id: 'US2024283947FPP',
        },
        {
            sector: ['Forestry', 'Wood Products'],
            name: 'SOUTHERN TIMBER EXTRACTS MANUFACTURING CO., INC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 30.723197,
                lng: -88.07836170000002,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '542 BARTON ST S, MOBILE, AL, 36610-4740',
            os_id: 'US2024300WEAJMD',
        },
        {
            sector: ['Apparel'],
            name: 'Eagle Manufacturing Co.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 36.1953095,
                lng: -86.78789739999999,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '230 Cumberland Bend, Nashville, Tennessee, United States of America',
            os_id: 'US2020133EPKZDP',
        },
        {
            sector: ['Health', 'Medical Equipment & Services'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'Denso Manufacturing Tennessee, Inc',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.7620477,
                lng: -84.0033316,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '1720 Robert C Jackson Dr Maryville, Tennessee 37801',
            os_id: 'US2024212J3HQM6',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'SILGAN CONTAINERS MANUFACTURING CORP',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.96,
                lng: -88.95,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '1226 S MANUFACTURERS ROW, TRENTON TENNESSEE 38382 (GIBSON)',
            os_id: 'US20242124FQ414',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            name: 'VESTAL MANUFACTURING ENTERPRISES INC.',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.605,
                lng: -84.454,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address:
                '177 INDUSTRIAL PARK RD, SWEETWATER TENNESSEE 37874 (MONROE)',
            os_id: 'US2024213ATXCX0',
        },
        {
            sector: ['Chemicals', 'Commodities', 'Waste Management'],
            location_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
            name: 'DENSO MANUFACTURING ATHENS TENNESSEE INC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.474,
                lng: -84.644,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '2400 2406 2408 DENSO DR, ATHENS TENNESSEE 37303 (MCMINN)',
            os_id: 'US2024212G2QAV3',
            processing_type: [
                'Onsite Chemical Disposal',
                'Offsite Chemical Disposal',
            ],
        },
        {
            sector: ['Tobacco Products'],
            name: 'A.C.E. Manufacturing, LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 42.3616725,
                lng: -87.8309903,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '119 N Genesee St Waukegan, Illinois 60085',
            os_id: 'US2024280P32ENR',
        },
        {
            sector: ['Health', 'Medical Equipment & Services'],
            name: 'Big River Engineering and Manufacturing',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.1462187,
                lng: -90.0468369,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '85 N 4th St Memphis, Tennessee 38103',
            os_id: 'US2024281FXYVBB',
        },
        {
            sector: ['Health', 'Medical Equipment & Services'],
            name: 'Eaton Manufacturing Corporation Dba Eaton Medical',
            parent_company: 'Eaton Manufacturing Corporation',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 35.1235658,
                lng: -90.01545349999999,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '1401 Heistan Pl Memphis, Tennessee 38104',
            os_id: 'US202428635MMXD',
        },
        {
            sector: ['Food'],
            name: 'St. Lawrence County Manufacturing and Properties, LLC',
            claim_status: 'unclaimed',
            coordinates: {
                lat: 44.5896342,
                lng: -75.173701,
            },
            country: {
                name: 'United States',
                numeric: '840',
                alpha_3: 'USA',
                alpha_2: 'US',
            },
            address: '30 Buck St Canton, New York 13617',
            os_id: 'US2024286MWYBMD',
        },
    ],
};

export function fetchProductionLocations() {
    return async dispatch => {
        dispatch(startFetchProductionLocations());

        // TODO: Replace the mock implementation with an actual API call
        // as part of https://opensupplyhub.atlassian.net/browse/OSDEV-1374
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

export function fetchProductionLocationByOsId(osID) {
    return async dispatch => {
        dispatch(startFetchSingleProductionLocation());

        try {
            const { data } = await apiRequest.get(
                makeGetProductionLocationURL(osID),
            );
            return dispatch(completeFetchSingleProductionLocation(data));
        } catch (err) {
            return dispatch(
                logErrorAndDispatchFailure(
                    err,
                    'An error prevented fetching data about that production location',
                    failFetchSingleProductionLocation,
                ),
            );
        }
    };
}
