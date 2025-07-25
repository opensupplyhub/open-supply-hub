import querystring from 'querystring';
import get from 'lodash/get';
import isArray from 'lodash/isArray';
import isObject from 'lodash/isObject';
import flatten from 'lodash/flatten';
import identity from 'lodash/identity';
import split from 'lodash/split';
import last from 'lodash/last';
import snakeCase from 'lodash/snakeCase';
import some from 'lodash/some';
import size from 'lodash/size';
import negate from 'lodash/negate';
import omitBy from 'lodash/omitBy';
import isEmpty from 'lodash/isEmpty';
import isNumber from 'lodash/isNumber';
import isString from 'lodash/isString';
import isNil from 'lodash/isNil';
import intersection from 'lodash/intersection';
import values from 'lodash/values';
import flow from 'lodash/flow';
import noop from 'lodash/noop';
import compact from 'lodash/compact';
import startsWith from 'lodash/startsWith';
import head from 'lodash/head';
import replace from 'lodash/replace';
import trimEnd from 'lodash/trimEnd';
import trim from 'lodash/trim';
import range from 'lodash/range';
import ceil from 'lodash/ceil';
import toInteger from 'lodash/toInteger';
import keys from 'lodash/keys';
import pickBy from 'lodash/pickBy';
import every from 'lodash/every';
import uniqWith from 'lodash/uniqWith';
import filter from 'lodash/filter';
import includes from 'lodash/includes';
import join from 'lodash/join';
import map from 'lodash/map';
import mapValues from 'lodash/mapValues';
import mapKeys from 'lodash/mapKeys';
import uniq from 'lodash/uniq';
import startCase from 'lodash/startCase';
import toLower from 'lodash/toLower';
import { isURL, isInt } from 'validator';
import { featureCollection, bbox } from '@turf/turf';
import hash from 'object-hash';
import * as XLSX from 'xlsx';
import moment from 'moment';
import removeAccents from 'remove-accents';
import unidecode from 'unidecode';
import { v4 as uuidv4 } from 'uuid';
import {
    object as objectYup,
    string as stringYup,
    array as arrayYup,
} from 'yup';

import {
    OTHER,
    FEATURE_COLLECTION,
    CLAIM_A_FACILITY,
    inputTypesEnum,
    registrationFieldsEnum,
    registrationFormFields,
    profileFormFields,
    facilitiesRoute,
    dashboardRoute,
    DEFAULT_PAGE,
    DEFAULT_ROWS_PER_PAGE,
    ENTER_KEY,
    facilityListStatusChoicesEnum,
    facilityClaimStatusChoices,
    facilityListItemStatusChoicesEnum,
    facilityListItemErrorStatuses,
    facilityListSummaryStatusMessages,
    minimum100PercentWidthEmbedHeight,
    matchResponsibilityEnum,
    optionsForSortingResults,
    componentsWithErrorMessage,
    listParsingErrorMappings,
    MODERATION_QUEUE,
    MODERATION_STATUS_COLORS,
    DATA_SOURCES_ENUM,
    API_V1_ERROR_REQUEST_SOURCE_ENUM,
    SLC_FORM_CONSTRAINTS,
} from './constants';

import renderUniqueListItems from './renderUtils';
import { createListItemCSV } from './util.listItemCSV';
import { createFacilitiesCSV, formatDataForCSV } from './util.facilitiesCSV';
import formatFacilityClaimsDataForXLSX from './util.facilityClaimsXLSX';
import formatModerationEventsDataForXLSX from './util.moderationEventsXLSX';
import COLOURS from './COLOURS';

export function DownloadXLSX(data, fileName) {
    import('file-saver').then(({ saveAs }) => {
        saveAs(
            new Blob([data], { type: 'application/octet-stream' }),
            fileName,
        );
        return noop();
    });
}

export function DownloadCSV(data, fileName) {
    import('file-saver').then(({ saveAs }) => {
        saveAs(new Blob([data], { type: 'text/csv;charset=utf-8;' }), fileName);
        return noop();
    });
}

export const downloadListItemCSV = (list, items) =>
    DownloadCSV(
        createListItemCSV(items),
        `${list.id}_${list.name}_${new Date().toLocaleDateString()}.csv`,
    );

export const downloadFacilitiesCSV = facilities =>
    DownloadCSV(createFacilitiesCSV(facilities), 'facilities.csv');

export const createXLSX = (dataToConvert, formatData, worksheetName) => {
    const data = formatData(dataToConvert);
    const worksheet = XLSX.utils.aoa_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, worksheetName);
    const wopts = { bookType: 'xlsx', bookSST: false, type: 'array' };
    return XLSX.write(workbook, wopts);
};

export const downloadFacilitiesXLSX = facilities =>
    DownloadXLSX(
        createXLSX(facilities, formatDataForCSV, 'facilities'),
        'facilities.xlsx',
    );

export const downloadFacilityClaimsXLSX = facilityClaims =>
    DownloadXLSX(
        createXLSX(
            facilityClaims,
            formatFacilityClaimsDataForXLSX,
            'Facility claims',
        ),
        'facility_claims.xlsx',
    );

export const downloadModerationEventsXLSX = moderationEvents =>
    DownloadXLSX(
        createXLSX(
            moderationEvents,
            formatModerationEventsDataForXLSX,
            'Moderation events',
        ),
        'moderation_events.xlsx',
    );

export const makeUserLoginURL = () => '/user-login/';
export const makeUserLogoutURL = () => '/user-logout/';
export const makeUserSignupURL = () => '/user-signup/';
export const makeUserConfirmEmailURL = () =>
    '/rest-auth/registration/verify-email/';

export const makeUploadFacilityListsURL = () => '/api/facility-lists/';
export const makeFacilityListsURL = () => '/api/facility-lists/';
export const makeSingleFacilityListURL = id => `/api/facility-lists/${id}/`;
export const makeSingleFacilityListItemsURL = id =>
    `/api/facility-lists/${id}/items/`;

export const createRemoveFacilityListItemURL = listID =>
    `/api/facility-lists/${listID}/remove/`;

export const makeApproveFacilityListURL = listID =>
    `/api/facility-lists/${listID}/approve/`;

export const makeRejectFacilityListURL = listID =>
    `/api/facility-lists/${listID}/reject/`;

export const makeDashboardFacilityListsURL = () => '/api/admin-facility-lists/';

export const makeDashboardApiBlocksURL = () => '/api/api-blocks/';
export const makeDashboardApiBlockURL = id => `/api/api-blocks/${id}/`;

export const makeDashboardGeocoderURL = () => '/api/geocoder/';
export const makeClaimGeocoderURL = id => `/api/facility-claims/${id}/geocode/`;

export const makeDashboardActivityReportsURL = () =>
    '/api/facility-activity-reports/';
export const makeRejectDashboardActivityReportURL = id =>
    `/api/facility-activity-reports/${id}/reject/`;
export const makeConfirmDashboardActivityReportURL = id =>
    `/api/facility-activity-reports/${id}/approve/`;
export const makeCreateDashboardActivityReportURL = osId =>
    `/api/facilities/${osId}/report/`;

export const makeAPITokenURL = () => '/api-token-auth/';

export const makeUserAPIInfoURL = uid => `/user-api-info/${uid}/`;

export const makeGetContributorsURL = () => '/api/contributors/';
export const makeGetListsURL = () => '/api/contributor-lists/';
export const makeGetSortedListsURL = () => '/api/contributor-lists-sorted/';
export const makeGetContributorTypesURL = () => '/api/contributor-types/';
export const makeGetCountriesURL = () => '/api/countries/';
export const makeGetSectorsURL = options =>
    options && options.embed
        ? `/api/sectors?contributor=${options.contributor}&embed=${options.embed}`
        : '/api/sectors/';
export const makeGetGroupedSectorsURL = () => '/api/sectors/?grouped=true';
export const makeGetParentCompaniesURL = () => '/api/parent-companies/';
export const makeGetFacilitiesTypeProcessingTypeURL = () =>
    '/api/facility-processing-types/';
export const makeGetNumberOfWorkersURL = () => '/api/workers-ranges/';
export const makeGetNativeLanguageName = () => '/api/native_language_name/';
export const makeGetClaimStatusesURL = () => '/api/claim-statuses/';

export const makeGetFacilitiesURL = () => '/api/facilities/';
export const makeGetFacilityByOSIdURL = (
    osId,
    useCreatedAtForDataPoints = false,
) =>
    `/api/facilities/${osId}/?created_at_of_data_points=${useCreatedAtForDataPoints}&pending_claim_info=true`;
export const makeGetFacilityByOSIdURLWithContributorId = (
    osId,
    embed,
    contributorId,
    useCreatedAtForDataPoints,
) =>
    `/api/facilities/${osId}/?embed=${embed}&contributor=${contributorId}&created_at_of_data_points=${useCreatedAtForDataPoints}&pending_claim_info=true`;
export const makeGetFacilitiesURLWithQueryString = (qs, pageSize) =>
    `/api/facilities/?${qs}&number_of_public_contributors=true&pageSize=${pageSize}`;
export const makeGetFacilitiesDownloadURLWithQueryString = (qs, pageSize) =>
    `/api/facilities-downloads/?${qs}&pageSize=${pageSize}`;
export const makeGetDownloadLocationsCheckoutSessionURL = () =>
    '/api/v1/download-locations-checkout-session/';
export const makeClaimFacilityAPIURL = osId => `/api/facilities/${osId}/claim/`;
export const makeSplitFacilityAPIURL = osID => `/api/facilities/${osID}/split/`;
export const makeTransferFacilityAPIURL = osID =>
    `/api/facilities/${osID}/move/`;
export const makePromoteFacilityMatchAPIURL = osID =>
    `/api/facilities/${osID}/promote/`;
export const makeLinkFacilityAPIURL = osID => `/api/facilities/${osID}/link/`;

export const makeMergeTwoFacilitiesAPIURL = (targetOSID, toMergeOSID) =>
    `/api/facilities/merge/?target=${targetOSID}&merge=${toMergeOSID}`;

export const makeGetFacilitiesCountURL = () => '/api/facilities/count/';

export const makeGetAPIFeatureFlagsURL = () => '/api-feature-flags/';

export const makeGetFacilityClaimsURLWithQueryString = qs =>
    `/api/facility-claims/?${qs}`;
export const makeGetFacilityClaimByClaimIDURL = claimID =>
    `/api/facility-claims/${claimID}/`;
export const makeMessageFacilityClaimantByClaimIDURL = claimID =>
    `/api/facility-claims/${claimID}/message-claimant/`;
export const makeApproveFacilityClaimByClaimIDURL = claimID =>
    `/api/facility-claims/${claimID}/approve/`;
export const makeDenyFacilityClaimByClaimIDURL = claimID =>
    `/api/facility-claims/${claimID}/deny/`;
export const makeRevokeFacilityClaimByClaimIDURL = claimID =>
    `/api/facility-claims/${claimID}/revoke/`;
export const makeAddNewFacilityClaimReviewNoteURL = claimID =>
    `/api/facility-claims/${claimID}/note/`;

export const makeGetOrUpdateApprovedFacilityClaimURL = claimID =>
    `/api/facility-claims/${claimID}/claimed/`;
export const makeGetClaimedFacilitiesURL = () => '/api/facilities/claimed/';
export const makeClaimedFacilityDetailsLink = claimID => `/claimed/${claimID}/`;

export const makeLogDownloadUrl = (path, recordCount) =>
    `/api/log-download/?path=${path}&record_count=${recordCount}`;

export const makeUpdateFacilityLocationURL = osID =>
    `/api/facilities/${osID}/update-location/`;

export const makeEmbedConfigURL = id =>
    `/api/embed-configs/${id ? `${id}/` : ''}`;
export const makeContributorEmbedConfigURL = contributorId =>
    `/api/contributor-embed-configs/${contributorId}/`;
export const makeNonStandardFieldsURL = () => '/api/nonstandard-fields/';

export const makeProductionLocationURL = (osID = '') => {
    const osIDPathParameter = osID ? `${osID}/` : '';
    return `/api/v1/production-locations/${osIDPathParameter}`;
};

export const makeGetProductionLocationsForPotentialMatches = (
    productionLocationName,
    address,
    countryCode,
    limit,
) => {
    const params = new URLSearchParams();

    if (productionLocationName) params.append('name', productionLocationName);
    if (address) params.append('address', address);
    if (countryCode) params.append('country', countryCode);
    if (limit) params.append('size', limit);

    return `/api/v1/production-locations/?${params.toString()}`;
};

export const makeModerationEventRecordURL = moderationID =>
    `/api/v1/moderation-events/${moderationID}/`;

export const makeProductionLocationFromModerationEventURL = (
    moderationID,
    osID = '',
) => {
    const osIDPathParameter = osID ? `${osID}/` : '';
    return `/api/v1/moderation-events/${moderationID}/production-locations/${osIDPathParameter}`;
};

export const makeContributeProductionLocationUpdateURL = osID =>
    `/contribute/single-location/${osID}/info/`;

export const makeGetModerationEventsWithQueryString = (
    qs,
    page,
    pageSize,
    sortBy,
    orderBy,
) =>
    `/api/v1/moderation-events/?${qs}&sort_by=${sortBy}&order_by=${orderBy}&from=${
        page * pageSize
    }&size=${pageSize}`;

export const getValueFromObject = ({ value }) => value;

const createCompactSortedQuerystringInputObject = (inputObject = []) =>
    compact(inputObject.map(getValueFromObject).slice().sort());

export const createQueryStringFromModerationQueueFilters = (
    { dataSources = [], moderationStatuses = [], countries = [] },
    afterDate = '',
    beforeDate = '',
) => {
    const createRepeatedKeys = (key, valueArr) =>
        valueArr.map(value => `${key}=${encodeURIComponent(value)}`).join('&');

    const inputForQueryString = Object.freeze({
        source: dataSources,
        status: moderationStatuses,
        country: countries,
        date_gte: afterDate,
        date_lt: beforeDate,
    });

    return Object.entries(inputForQueryString)
        .reduce((acc, [key, value]) => {
            if (value && (Array.isArray(value) ? value.length > 0 : true)) {
                if (Array.isArray(value)) {
                    acc.push(
                        createRepeatedKeys(
                            key,
                            createCompactSortedQuerystringInputObject(value),
                        ),
                    );
                } else {
                    acc.push(`${key}=${encodeURIComponent(value)}`);
                }
            }
            return acc;
        }, [])
        .join('&');
};

export const createQueryStringFromSearchFilters = (
    {
        facilityFreeTextQuery = '',
        contributors = [],
        contributorTypes = [],
        countries = [],
        sectors = [],
        parentCompany = [],
        facilityType = [],
        processingType = [],
        productType = [],
        numberOfWorkers = [],
        nativeLanguageName = '',
        lists = [],
        combineContributors = '',
        boundary = {},
        sortAlgorithm = {},
        claimStatuses = [],
    },
    withEmbed,
    detail,
) => {
    const inputForQueryString = Object.freeze({
        q: facilityFreeTextQuery,
        contributors: createCompactSortedQuerystringInputObject(contributors),
        lists: createCompactSortedQuerystringInputObject(lists),
        contributor_types: createCompactSortedQuerystringInputObject(
            contributorTypes,
        ),
        countries: createCompactSortedQuerystringInputObject(countries),
        statuses: createCompactSortedQuerystringInputObject(claimStatuses),
        sectors: createCompactSortedQuerystringInputObject(sectors),
        parent_company: createCompactSortedQuerystringInputObject(
            parentCompany,
        ),
        facility_type: createCompactSortedQuerystringInputObject(facilityType),
        processing_type: createCompactSortedQuerystringInputObject(
            processingType,
        ),
        product_type: createCompactSortedQuerystringInputObject(productType),
        number_of_workers: createCompactSortedQuerystringInputObject(
            numberOfWorkers,
        ),
        native_language_name: nativeLanguageName,
        combine_contributors: combineContributors,
        boundary: isEmpty(boundary) ? '' : JSON.stringify(boundary),
        sort_by: isEmpty(sortAlgorithm) ? '' : sortAlgorithm.value,
        embed: !withEmbed ? '' : '1',
        detail: detail ? 'true' : undefined,
    });

    return querystring.stringify(omitBy(inputForQueryString, isEmpty));
};

export const mapParamToReactSelectOption = param => {
    if (isEmpty(param)) {
        return null;
    }

    if (Number(param)) {
        return Object.freeze({
            value: Number(param),
            label: param,
        });
    }

    return Object.freeze({
        value: param,
        label: param,
    });
};

export const createSelectOptionsFromParams = params => {
    const paramsInArray = !isArray(params) ? [params] : params;

    // compact to remove empty values from querystring params like 'countries='
    return compact(
        Object.freeze(paramsInArray.map(mapParamToReactSelectOption)),
    );
};

export const getAlgorithm = sortBy =>
    optionsForSortingResults.filter(el => el.value === sortBy)[0] ??
    optionsForSortingResults[0];

export const createFiltersFromQueryString = qs => {
    const qsToParse = startsWith(qs, '?') ? qs.slice(1) : qs;

    const {
        q: facilityFreeTextQuery = '',
        contributors = [],
        lists = [],
        contributor_types: contributorTypes = [],
        countries = [],
        sectors = [],
        statuses = [],
        parent_company: parentCompany = [],
        facility_type: facilityType = [],
        processing_type: processingType = [],
        product_type: productType = [],
        number_of_workers: numberOfWorkers = [],
        native_language_name: nativeLanguageName = '',
        combine_contributors: combineContributors = '',
        boundary = '',
        sort_by: sortBy = '',
    } = querystring.parse(qsToParse);

    return Object.freeze({
        facilityFreeTextQuery,
        contributors: createSelectOptionsFromParams(contributors),
        lists: createSelectOptionsFromParams(lists),
        contributorTypes: createSelectOptionsFromParams(contributorTypes),
        countries: createSelectOptionsFromParams(countries),
        statuses: createSelectOptionsFromParams(statuses),
        sectors: createSelectOptionsFromParams(sectors),
        parentCompany: createSelectOptionsFromParams(parentCompany),
        facilityType: createSelectOptionsFromParams(facilityType),
        processingType: createSelectOptionsFromParams(processingType),
        productType: createSelectOptionsFromParams(productType),
        numberOfWorkers: createSelectOptionsFromParams(numberOfWorkers),
        nativeLanguageName,
        combineContributors,
        boundary: isEmpty(boundary) ? null : JSON.parse(boundary),
        sortAlgorithm: getAlgorithm(sortBy),
    });
};

export const getNumberFromParsedQueryStringParamOrUseDefault = (
    inputValue,
    defaultValue,
) => {
    if (!inputValue) {
        return defaultValue;
    }

    const nonArrayValue = isArray(inputValue) ? head(inputValue) : inputValue;

    return Number(nonArrayValue) || defaultValue;
};

export const createPaginationOptionsFromQueryString = qs => {
    const qsToParse = startsWith(qs, '?') ? qs.slice(1) : qs;

    const { page, rowsPerPage } = querystring.parse(qsToParse);

    return Object.freeze({
        page: getNumberFromParsedQueryStringParamOrUseDefault(
            page,
            DEFAULT_PAGE,
        ),
        rowsPerPage: getNumberFromParsedQueryStringParamOrUseDefault(
            rowsPerPage,
            DEFAULT_ROWS_PER_PAGE,
        ),
    });
};

export const createParamsFromQueryString = qs => {
    const qsToParse = startsWith(qs, '?') ? qs.slice(1) : qs;

    const { search, status } = querystring.parse(qsToParse);

    const params = {};

    if (status) {
        params.status = Array.isArray(status) ? status : [status];
    }

    if (search) {
        params.search = search;
    }

    return params;
};

export const getTokenFromQueryString = qs => {
    const qsToParse = startsWith(qs, '?') ? qs.slice(1) : qs;

    const { token = '' } = querystring.parse(qsToParse);

    return isArray(token) ? head(token) : token;
};

const parseFilterQueryString = qs => (startsWith(qs, '?') ? qs.slice(1) : qs);

export const dashboardListParamsDefaults = Object.freeze({
    contributor: null,
    matchResponsibility: matchResponsibilityEnum.MODERATOR,
    status: facilityListStatusChoicesEnum.PENDING,
});

export const getDashboardListParamsFromQueryString = qs => {
    const {
        contributor,
        matchResponsibility = dashboardListParamsDefaults.matchResponsibility,
        status = dashboardListParamsDefaults.status,
    } = querystring.parse(parseFilterQueryString(qs));

    return Object.freeze({
        contributor: getNumberFromParsedQueryStringParamOrUseDefault(
            contributor,
            null,
        ),
        matchResponsibility,
        status,
    });
};

export const dashboardClaimsListParamsDefaults = Object.freeze({
    countries: [],
    claimStatuses: facilityClaimStatusChoices[0].value,
});

export const getDashboardClaimsListParamsFromQueryString = qs => {
    const {
        countries,
        statuses = dashboardClaimsListParamsDefaults.claimStatuses,
    } = querystring.parse(parseFilterQueryString(qs));

    const statusesArray = Array.isArray(statuses) ? statuses : [statuses];
    const countriesArray = Array.isArray(countries) ? countries : [countries];

    return Object.freeze({
        countries: uniq(compact(countriesArray)),
        statuses: intersection(
            uniq(compact(statusesArray)),
            map(facilityClaimStatusChoices, 'value'),
        ),
    });
};

export const createTileURLWithQueryString = (qs, key, grid = true) =>
    `/tile/${
        grid ? 'facilitygrid' : 'facilities'
    }/${key}/{z}/{x}/{y}.pbf`.concat(isEmpty(qs) ? '' : `?${qs}`);

export const createTileCacheKeyWithEncodedFilters = (filters, key) =>
    `${key}-${hash(filters).slice(0, 8)}`;

export const allFiltersAreEmpty = filters =>
    values(filters).reduce((acc, next) => {
        if (!isEmpty(next)) {
            return false;
        }

        return acc;
    }, true);

export const getFeaturesFromFeatureCollection = ({ features }) => features;

export const createErrorListFromResponseObject = data =>
    flatten(
        Object.entries(data).map(([field, errors]) => {
            if (isArray(errors)) {
                return errors.map(err => `${field}: ${err}`);
            }

            return [];
        }),
    );

export function logErrorAndDispatchFailure(
    error,
    defaultMessage,
    failureAction,
) {
    return dispatch => {
        const response = get(error, 'response', { data: null, status: null });

        if (!response.status || response.status >= 500) {
            window.console.warn(error);
            return dispatch(failureAction([defaultMessage]));
        }

        if (response.status === 404) {
            window.console.warn(error);
            return dispatch(failureAction(['Not found']));
        }

        const errorMessages = (() => {
            if (!response || !response.data) {
                return [defaultMessage];
            }

            // For signin-error
            if (response.data.non_field_errors) {
                return response.data.non_field_errors;
            }

            if (isArray(response.data)) {
                return response.data;
            }

            if (response.data.detail) {
                return [response.data.detail];
            }

            if (isObject(response.data)) {
                return createErrorListFromResponseObject(response.data);
            }

            return [defaultMessage];
        })();

        return dispatch(failureAction(errorMessages));
    };
}

export const logErrorAndDispatchFailureApiV1 = (
    error,
    defaultMessage,
    failureAction,
) => dispatch => {
    const { response } = error || {};
    const { status, data } = response || {};
    const errorObj = {
        errorSource: null,
        detail: defaultMessage,
        errors: null,
        rawData: null,
    };

    if (status && data) {
        if (status >= 400 && status <= 499) {
            errorObj.errorSource = API_V1_ERROR_REQUEST_SOURCE_ENUM.CLIENT;
            errorObj.detail = data.detail;
            errorObj.rawData = data;

            if (isArray(data.errors) && !isEmpty(data.errors)) {
                errorObj.errors = data.errors;
            }

            return dispatch(failureAction(errorObj));
        }

        if (status >= 500 && status <= 599) {
            errorObj.errorSource = API_V1_ERROR_REQUEST_SOURCE_ENUM.SERVER;
            errorObj.rawData = data;

            // Field "detail" and "errors" aren't always present in the V1 API
            // response for 500 errors. In case of an unexpected error, it may
            // return a different structure, such as HTML.
            if (isString(data.detail) && !isEmpty(data.detail)) {
                errorObj.detail = data.detail;

                if (isArray(data.errors) && !isEmpty(data.errors)) {
                    errorObj.errors = data.errors;
                }
            }

            window.console.warn(error);
            return dispatch(failureAction(errorObj));
        }
    }

    window.console.warn(error);
    return dispatch(failureAction(errorObj));
};

export const getValueFromEvent = ({ target: { value } }) => value;

export const getIDFromEvent = ({ target: { id } }) => id;

export const getCheckedFromEvent = ({ target: { checked } }) => checked;

export const getFileFromInputRef = inputRef =>
    get(inputRef, 'current.files[0]', null);

export const getFileNameFromInputRef = inputRef =>
    get(inputRef, 'current.files[0].name', '');

const makeCreateFormErrorMessagesFn = fields => form =>
    fields.reduce((acc, { id, label, required }) => {
        if (!required) {
            return acc;
        }

        if (form[id]) {
            return acc;
        }

        const missingFieldMessage = `Missing required field ${label}`;

        if (id === registrationFieldsEnum.otherContributorType) {
            return form[registrationFieldsEnum.contributorType] === OTHER
                ? acc.concat(missingFieldMessage)
                : acc;
        }

        return acc.concat(missingFieldMessage);
    }, []);

export const createSignupErrorMessages = makeCreateFormErrorMessagesFn(
    registrationFormFields,
);
export const createProfileUpdateErrorMessages = makeCreateFormErrorMessagesFn(
    profileFormFields,
);

export function createUploadFormErrorMessages(name, file) {
    const allowedCharsRegex = /^[a-zA-Z0-9\s'&,.()[\]-]+$/;
    const restrictedCharsRegex = /^[0-9&.'()[\]-]+$/;

    const errorMessages = [];

    if (!name) {
        errorMessages.push(componentsWithErrorMessage.missingListName);
    } else {
        // Didn't allow name with invalid characters.
        if (!allowedCharsRegex.test(name)) {
            errorMessages.push(componentsWithErrorMessage.invalidCharacters);
        }
        // Didn't allow name that consists only of symbols or numbers.
        if (restrictedCharsRegex.test(name)) {
            errorMessages.push(componentsWithErrorMessage.mustConsistOfLetters);
        }
    }

    if (!file) {
        errorMessages.push(componentsWithErrorMessage.missingFile);
    }

    return errorMessages;
}

const makeCreateFormRequestDataFn = fields => form =>
    fields.reduce(
        (acc, { id, modelFieldName }) =>
            Object.assign({}, acc, {
                [modelFieldName]: form[id],
            }),
        {},
    );

export const createSignupRequestData = makeCreateFormRequestDataFn(
    registrationFormFields,
);
export const createProfileUpdateRequestData = makeCreateFormRequestDataFn(
    profileFormFields,
);

export const getStateFromEventForEventType = Object.freeze({
    [inputTypesEnum.checkbox]: getCheckedFromEvent,
    [inputTypesEnum.select]: identity,
    [inputTypesEnum.text]: getValueFromEvent,
    [inputTypesEnum.password]: getValueFromEvent,
});

const mapSingleChoiceToSelectOption = ([value, label]) =>
    Object.freeze({
        value,
        label,
    });

const mapSingleDictChoiceToSelectOption = dict =>
    Object.freeze({
        value: dict.id,
        label: dict.name,
    });

export const mapDjangoChoiceTuplesToSelectOptions = data =>
    Object.freeze(data.map(mapSingleChoiceToSelectOption));

export const mapDjangoChoiceDictToSelectOptions = data =>
    Object.freeze(data.map(mapSingleDictChoiceToSelectOption));

const mapSingleChoiceValueToSelectOption = value =>
    Object.freeze({
        value,
        label: value,
    });

export const mapDjangoChoiceTuplesValueToSelectOptions = data =>
    Object.freeze(data.map(mapSingleChoiceValueToSelectOption));

export const mapProcessingTypeOptions = (fPTypes, fTypes) => {
    let pTypes = [];
    if (fTypes.length === 0) {
        pTypes = fPTypes.map(type => type.processingTypes).flat();
    } else {
        // When there are facility types, only return the
        // processing types that are under those facility types
        fTypes.forEach(fType => {
            fPTypes.forEach(fPType => {
                if (fType.value === fPType.facilityType) {
                    pTypes = pTypes.concat(fPType.processingTypes);
                }
            });
        });
    }
    return mapDjangoChoiceTuplesValueToSelectOptions(uniq(pTypes.sort()));
};

export const mapFacilityTypeOptions = (fPTypes, pTypes) => {
    let fTypes = [];
    if (pTypes.length === 0) {
        fTypes = fPTypes.map(type => type.facilityType);
    } else {
        // When there are processing types, only return the
        // facility types that have those processing types
        pTypes.forEach(pType => {
            fPTypes.forEach(fPType => {
                if (fPType.processingTypes.includes(pType.value)) {
                    fTypes = fTypes.concat(fPType.facilityType);
                }
            });
        });
    }
    return mapDjangoChoiceTuplesValueToSelectOptions(uniq(fTypes.sort()));
};

export const mapSectorGroupsToSelectOptions = data =>
    Object.freeze(
        data.map(group => ({
            label: group.group_name,
            options: group.sectors.map(sector => ({
                groupLabel: group.group_name,
                value: sector,
                label: sector,
            })),
        })),
    );

export const allListsAreEmpty = (...lists) => negate(some)(lists, size);

export const makeFacilityDetailLink = (osID, search) =>
    `${facilitiesRoute}/${osID}${search || ''}`;

export const makeClaimFacilityLink = osID => `${facilitiesRoute}/${osID}/claim`;

export const makeApprovedClaimDetailsLink = claimID => `/claimed/${claimID}`;

export const makeFacilityClaimDetailsLink = claimID =>
    `/dashboard/claims/${claimID}`;

export const makeContributionRecordLink = moderationID =>
    `/dashboard/moderation-queue/${moderationID}`;

export const makeDashboardContributorListLink = ({
    contributorID,
    matchResponsibility,
    status,
    page,
    rowsPerPage,
}) => {
    const getQuery = (
        value,
        field,
        initial = dashboardListParamsDefaults[field],
    ) => (value && value !== initial ? `${field}=${value}` : '');
    const params = [
        getQuery(contributorID, 'contributor'),
        getQuery(matchResponsibility, 'matchResponsibility'),
        getQuery(status, 'status'),
        getQuery(page, 'page', DEFAULT_PAGE),
        getQuery(rowsPerPage, 'rowsPerPage', DEFAULT_ROWS_PER_PAGE),
    ].filter(p => !!p);
    return `/dashboard/lists/${
        params.length > 0 ? `?${params.join('&')}` : ''
    }`;
};

export const makeDashboardClaimListLink = ({ statuses, countries }) => {
    const createClaimFilterParams = (key, claimParamValues) =>
        claimParamValues && claimParamValues.length > 0
            ? join(
                  map(claimParamValues, value => `${key}=${value}`),
                  '&',
              )
            : '';

    const statusParams = createClaimFilterParams('statuses', statuses);
    const countryParams = createClaimFilterParams('countries', countries);

    const params = [statusParams, countryParams]
        .filter(param => param)
        .join('&');

    return params ? `/dashboard/claims/?${params}` : '/dashboard/claims';
};

export const splitContributorsIntoPublicAndNonPublic = contributors =>
    contributors.reduce(
        (splittedContributors, currentContributor) => {
            if (currentContributor.id) {
                const index = splittedContributors.publicContributors.findIndex(
                    publicContributor =>
                        publicContributor.id === currentContributor.id,
                );
                if (index === -1) {
                    /*
                    Push the contributor to the array of public contributors if they don't
                    exist there. Also, the code replaces the list_name property with
                    list_names to make the object contain data more related to the
                    contributor and their lists, not one contribution of the contributor.
                    */
                    const {
                        list_name: listName,
                        ...contributorWithoutListName
                    } = currentContributor;
                    splittedContributors.publicContributors.push({
                        ...contributorWithoutListName,
                        list_names: [listName],
                    });
                } else {
                    /*
                    Group the name of the list under the contributor whose id already exists
                    in the array.
                    */
                    splittedContributors.publicContributors[
                        index
                    ].list_names.push(currentContributor.list_name);
                }
            } else {
                // If the object doesn't have the id key, it is a non-public contributor.
                splittedContributors.nonPublicContributors.push(
                    currentContributor,
                );
            }
            return splittedContributors;
        },
        {
            publicContributors: [],
            nonPublicContributors: [],
        },
    );

export const makeProfileRouteLink = userID => `/profile/${userID}`;

export const getBBoxForArrayOfGeoJSONPoints = flow(featureCollection, bbox);

export const makeApiBlockDetailLink = id => `/dashboard/apiblocks/${id}`;

export const makeFacilityListItemsDetailLink = id => `/lists/${id}`;
export const makePaginatedFacilityListItemsDetailLinkWithRowCount = (
    id,
    page,
    rowsPerPage,
    params,
) =>
    `/lists/${id}?${querystring.stringify(
        Object.assign({}, params, { page, rowsPerPage }),
    )}`;

export const makeSliceArgumentsForTablePagination = (page, rowsPerPage) =>
    Object.freeze([page * rowsPerPage, (page + 1) * rowsPerPage]);

export const makeDisputeClaimEmailLink = osId =>
    `mailto:claims@opensupplyhub.org?subject=Disputing a claim of facility ID ${osId}`;

export const makeReportADuplicateEmailLink = osId =>
    `mailto:data@opensupplyhub.org?subject=Reporting ID ${osId} as a duplicate facility`;

export const makeFeatureCollectionFromSingleFeature = feature =>
    Object.freeze({
        type: FEATURE_COLLECTION,
        features: Object.freeze([feature]),
    });

export const createConfirmFacilityListItemMatchURL = matchID =>
    `/api/facility-matches/${matchID}/confirm/`;

export const createRejectFacilityListItemMatchURL = matchID =>
    `/api/facility-matches/${matchID}/reject/`;

export const makeMyFacilitiesRoute = contributorID =>
    `/facilities/?contributors=${contributorID}`;

export const makeResetPasswordEmailURL = () => '/rest-auth/password/reset/';

export const makeResetPasswordConfirmURL = () =>
    '/rest-auth/password/reset/confirm/';

export const makeUserProfileURL = userID => `/user-profile/${userID}/`;

export const escapeCSVValue = value =>
    replace(replace(value, /"/g, '""'), /\n/g, ' ');

export const joinDataIntoCSVString = data =>
    data.reduce((csvAccumulator, nextRow) => {
        const joinedColumns = nextRow.reduce((rowAccumulator, nextColumn) => {
            if (isNumber(nextColumn)) {
                return rowAccumulator.concat(nextColumn, ',');
            }

            return rowAccumulator.concat(
                '' + '"' + escapeCSVValue(nextColumn) + '"', // eslint-disable-line
                ',',
            );
        }, '');

        return csvAccumulator.concat(trimEnd(joinedColumns, ','), '\n');
    }, '');

// Given a list where each item is like { label: 'ABCD', value: 123 }, and
// a payload which can be either:
// 1. A list of items like { label: '123', value: 123 }, or
// 2. A list of items where each item contains an `options` array, like:
//    { label: 'Category', options: [{ label: '123', value: 123 }, ...] },
// this function returns a list of items from the payload with their labels
// replaced by matching items found in the original list.
export const updateListWithLabels = (list, payload) =>
    list.reduce((accumulator, { value }) => {
        const flatPayload = payload.flatMap(item =>
            item.options ? item.options : item,
        );

        const validOption = flatPayload.find(
            ({ value: otherValue }) => value === otherValue,
        );

        if (!validOption) {
            return accumulator;
        }

        return accumulator.concat(
            Object.freeze({
                value,
                label: validOption.label,
            }),
        );
    }, []);

export const makeSubmitFormOnEnterKeyPressFunction = fn => ({ key }) => {
    if (key === ENTER_KEY) {
        return fn();
    }

    return noop();
};

export const makeFacilityListItemsRetrieveCSVItemsURL = (id, page) =>
    `${makeSingleFacilityListItemsURL(id)}?page=${page}&pageSize=100`;

export const makeFacilityListDataURLs = (id, count) => {
    const maxCount = toInteger(ceil(count, -2) / 100);

    return range(1, maxCount + 1).map(page =>
        makeFacilityListItemsRetrieveCSVItemsURL(id, page),
    );
};

export const makeFacilityListSummaryStatus = statuses => {
    const errorMessage = facilityListItemErrorStatuses.some(s =>
        statuses.includes(s),
    )
        ? facilityListSummaryStatusMessages.ERROR
        : '';
    const awaitingMessage = [
        facilityListItemStatusChoicesEnum.POTENTIAL_MATCH,
    ].some(s => statuses.includes(s))
        ? facilityListSummaryStatusMessages.AWAITING
        : '';
    const processingMessage = statuses.some(s =>
        [
            facilityListItemStatusChoicesEnum.UPLOADED,
            facilityListItemStatusChoicesEnum.PARSED,
            facilityListItemStatusChoicesEnum.GEOCODED,
            facilityListItemStatusChoicesEnum.GEOCODED_NO_RESULTS,
        ].includes(s),
    )
        ? facilityListSummaryStatusMessages.PROCESSING
        : '';
    const completeMessage = statuses.every(s =>
        [
            facilityListItemStatusChoicesEnum.MATCHED,
            facilityListItemStatusChoicesEnum.CONFIRMED_MATCH,
        ].includes(s),
    )
        ? facilityListSummaryStatusMessages.COMPLETED
        : '';

    return `${completeMessage}
            ${processingMessage}
            ${awaitingMessage}
            ${errorMessage}`
        .replace(/\s+/g, ' ')
        .trim();
};

export const addProtocolToWebsiteURLIfMissing = url => {
    if (startsWith(url, 'http://')) {
        return url;
    }

    if (startsWith(url, 'https://')) {
        return url;
    }

    return `http://${url}`;
};

export const filterFlagsIfAppIsEmbeded = (flags, isEmbeded) =>
    filter(flags, f => !isEmbeded || f !== 'claim_a_facility');

export const convertFeatureFlagsObjectToListOfActiveFlags = featureFlags =>
    keys(pickBy(featureFlags, identity));

export const checkWhetherUserHasDashboardAccess = user =>
    get(user, 'is_superuser', false);

export const isValidNumberOfWorkers = value => {
    if (isEmpty(value)) {
        return true;
    }

    const rangePattern = /^\d+-\d+$/;

    if (isInt(value.trim(), { min: 1, allow_leading_zeroes: false })) {
        return true;
    }

    if (rangePattern.test(value)) {
        const [start, end] = value.split('-');

        if (
            isInt(start.trim(), { min: 1, allow_leading_zeroes: false }) &&
            isInt(end.trim(), { min: 1, allow_leading_zeroes: false }) &&
            parseInt(start, 10) <= parseInt(end, 10)
        ) {
            return true;
        }
    }

    return false;
};

export const getNumberOfWorkersValidationError = value => {
    const valueOfZeroText =
        'The value of zero is not valid. Enter a positive whole number or a valid range (e.g., 1-5).';
    const rangePattern = /^\d+-\d+$/;

    if (parseInt(value, 10) === 0) {
        return valueOfZeroText;
    }

    const invalidFormatText =
        'Invalid format. Enter a whole number or a valid numeric range (e.g., 1-5).';

    if (!isInt(value, 10) && !rangePattern.test(value)) {
        return invalidFormatText;
    }

    const invalidEntryText = 'Invalid entry. The value cannot start from zero.';

    if (!rangePattern.test(value)) {
        return invalidEntryText;
    }

    const [start, end] = value.split('-');

    if (!isInt(end.trim(), { min: 1, allow_leading_zeroes: false })) {
        return valueOfZeroText;
    }

    const lessThenOrEqualText =
        'Invalid range. The minimum value must be less than or equal to the maximum value.';

    if (start >= end) {
        return lessThenOrEqualText;
    }

    return invalidEntryText;
};

export const claimAFacilityFormIsValid = ({
    yourName,
    yourTitle,
    yourBusinessWebsite,
    businessWebsite,
    businessLinkedinProfile,
    businessUploadFiles,
    numberOfWorkers,
}) =>
    every([!isEmpty(yourName), !isEmpty(yourTitle)], identity) &&
    some([isEmpty(yourBusinessWebsite), isURL(yourBusinessWebsite)]) &&
    isValidNumberOfWorkers(numberOfWorkers) &&
    every([
        isEmpty(businessWebsite) ||
            (!isEmpty(businessWebsite) && isURL(businessWebsite)),
        isEmpty(businessLinkedinProfile) ||
            (!isEmpty(businessLinkedinProfile) &&
                isURL(businessLinkedinProfile)),
        !isEmpty(businessUploadFiles) ||
            !isEmpty(businessWebsite) ||
            !isEmpty(businessLinkedinProfile),
    ]);

export const claimFacilitySupportDocsIsValid = ({
    yourName,
    yourTitle,
    yourBusinessWebsite,
    businessWebsite,
    businessLinkedinProfile,
    businessUploadFiles,
}) =>
    every([!isEmpty(yourName), !isEmpty(yourTitle)]) &&
    some([isEmpty(yourBusinessWebsite), isURL(yourBusinessWebsite)]) &&
    every([
        isEmpty(businessWebsite) ||
            (!isEmpty(businessWebsite) && isURL(businessWebsite)),
        isEmpty(businessLinkedinProfile) ||
            (!isEmpty(businessLinkedinProfile) &&
                isURL(businessLinkedinProfile)),
        !isEmpty(businessUploadFiles) ||
            !isEmpty(businessWebsite) ||
            !isEmpty(businessLinkedinProfile),
    ]);
export const isValidFacilityURL = url =>
    isEmpty(url) || isURL(url, { protocols: ['http', 'https'] });

export const anyListItemMatchesAreInactive = ({ matches }) =>
    some(matches, ['is_active', false]);

export const pluralizeResultsCount = count => {
    if (isNil(count)) {
        return null;
    }

    if (count === 1) {
        return '1 result';
    }

    return `${count} results`;
};

export const removeDuplicatesFromOtherLocationsData = otherLocationsData =>
    uniqWith(otherLocationsData, (location, otherLocation) => {
        const lat = get(location, 'lat', null);
        const lng = get(location, 'lng', null);
        const id = get(location, 'contributor_id', null);

        const otherLat = get(otherLocation, 'lat', null);
        const otherLng = get(otherLocation, 'lng', null);
        const otherID = get(otherLocation, 'contributor_id', null);

        if (lat !== otherLat || lng !== otherLng) {
            return false;
        }

        if ((!id && otherID) || (id && !otherID)) {
            return true;
        }

        if (id === otherID) {
            return true;
        }

        return false;
    });

export const getLocationWithoutEmbedParam = () =>
    window.location.href.replace('&embed=1', '').replace('embed=1', '');

export const getEmbeddedMapSrc = ({ contributor, timestamp }) => {
    const qs = timestamp
        ? querystring.stringify({
              contributors: contributor,
              embed: 1,
              timestamp,
          })
        : querystring.stringify({ contributors: contributor, embed: 1 });

    return window.location.href.replace('settings', `facilities?${qs}`);
};

// This must be kept in sync with renderEmbeddedMap in EmbeddedMapConfig.jsx
export const createIFrameHTML = ({ fullWidth, contributor, height, width }) =>
    fullWidth
        ? `<div>
               <style>
                   #oar-embed-0d4dc3a7-e3cd-4acc-88f0-422f5aeefa48 {
                       position: relative;
                       padding-top: ${height}%;
                   }
                   @media (max-width: 600px) { /* mobile breakpoint */
                       #oar-embed-0d4dc3a7-e3cd-4acc-88f0-422f5aeefa48 {
                           padding-top: ${minimum100PercentWidthEmbedHeight}
                       }
                   }
               </style>
               <div id="oar-embed-0d4dc3a7-e3cd-4acc-88f0-422f5aeefa48">
                   <iframe
                       src="${getEmbeddedMapSrc({
                           contributor,
                       })}"
                       frameborder="0"
                       allowfullscreen
                       style="position:absolute;top:0;
                              left:0;width:100%;height:100%;"
                       title="embedded-map">
                   </iframe>
               </div>
           </div>`
        : `<iframe
                src="${getEmbeddedMapSrc({
                    contributor,
                })}"
                frameBorder="0"
                style="width:${width}px;height:${height}px"
                title="embedded-map"
            />`;

export const getIsMobile = windowInnerWidth => windowInnerWidth < 600;

export const formatAttribution = (date, contributor) => {
    if (contributor) {
        return `${moment(date).format('LL')} by ${contributor}`;
    }
    return moment(date).format('LL');
};

export const createUserDropdownLinks = (
    user,
    logoutAction,
    activeFeatureFlags,
) => {
    const links = [];

    if (checkWhetherUserHasDashboardAccess(user)) {
        links.push(
            Object.freeze({
                label: 'Dashboard',
                href: dashboardRoute,
            }),
        );
    }

    if (includes(activeFeatureFlags, CLAIM_A_FACILITY)) {
        links.push(
            Object.freeze({
                label: 'My Facilities',
                href: '/claimed',
            }),
        );
    }

    links.push(
        Object.freeze({
            label: 'My Lists',
            href: '/lists',
        }),
        Object.freeze({
            label: 'Settings',
            href: '/settings',
        }),
        Object.freeze({
            label: 'Log Out',
            action: logoutAction,
        }),
    );

    return Object.freeze(links);
};

export const isApiUser = user =>
    !user.isAnon && Array.isArray(user.groups) && user.groups.length > 0;

export const logErrorToRollbar = (window, error, user) => {
    if (window.Rollbar) {
        if (user) {
            const contributorIdMsg = user.contributor_id
                ? ` (contributor id ${user.contributor_id})`
                : '';

            const userType = isApiUser(user) ? 'API user' : 'User';
            const rollbarErrMsg = `${userType}${contributorIdMsg}`;
            window.Rollbar.configure({
                payload: {
                    user: {
                        contributor_id: user.contributor_id,
                    },
                },
            });
            const rollbarError = new Error(`${rollbarErrMsg} ${error.message}`);
            Object.assign(rollbarError, error);

            window.Rollbar.error(rollbarError, {
                fingerprint: `${user.id}-${rollbarError.message}`,
            });
        } else {
            window.Rollbar.error(error);
        }
    }
};

function descendingComparator(a, b, orderBy) {
    let aValue = a[orderBy];
    let bValue = b[orderBy];

    if (typeof aValue === 'string') {
        aValue = removeAccents(aValue.toLowerCase());
    }
    if (typeof bValue === 'string') {
        bValue = removeAccents(bValue.toLowerCase());
    }

    if (aValue === null || bValue < aValue) {
        return -1;
    }
    if (bValue === null || bValue > aValue) {
        return 1;
    }
    return 0;
}

export function getComparator(order, orderBy) {
    return order === 'desc'
        ? (a, b) => descendingComparator(a, b, orderBy)
        : (a, b) => -descendingComparator(a, b, orderBy);
}

export function sort(array, comparator) {
    const stabilizedThis = array.map((el, index) => [el, index]);
    stabilizedThis.sort((a, b) => {
        const order = comparator(a[0], b[0]);
        if (order !== 0) {
            return order;
        }
        return a[1] - b[1];
    });
    return stabilizedThis.map(el => el[0]);
}

export const formatDate = (date, format) => moment(date).format(format);
export const formatUTCDate = (date, format) => moment.utc(date).format(format);

export const replaceListParsingErrorMessages = errors =>
    errors.map(
        ({ message, type }) => listParsingErrorMappings[type] || message,
    );

export const createOptionsFromConstants = constants =>
    Object.keys(constants).map(key =>
        Object.freeze({
            value: constants[key],
            label: constants[key],
        }),
    );

export const multiValueBackgroundHandler = (value, origin) => {
    if (origin === MODERATION_QUEUE) {
        return MODERATION_STATUS_COLORS[value] || 'default';
    }
    return COLOURS.MINT_GREEN;
};

export const openInNewTab = url => {
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
    if (newWindow) newWindow.opener = null;
};

const extractProductionLocationContributionValues = data => {
    if (isArray(data)) {
        return data.map(item => (item?.value ? item.value : item));
    }
    return data;
};

export const generateRangeField = value => {
    if (typeof value === 'number') {
        return { min: value, max: value };
    }

    if (typeof value === 'string' && value.includes('-')) {
        const [min, max] = value.split('-').map(Number);
        return max !== undefined ? { min, max } : { min };
    }

    return { min: Number(value), max: Number(value) };
};

const convertToSnakeFields = fields =>
    mapKeys(fields, (value, key) => snakeCase(key));

const filterNonEmptyFields = fields =>
    mapValues(
        pickBy(fields, value => !isEmpty(value)),
        extractProductionLocationContributionValues,
    );

export const parseContribData = contribData => {
    const { numberOfWorkers, country, ...fields } = contribData;
    const countryValue = country?.value;

    const parsedFields = convertToSnakeFields(filterNonEmptyFields(fields));

    return {
        ...parsedFields,
        ...(numberOfWorkers && {
            number_of_workers: generateRangeField(numberOfWorkers),
        }),
        country: countryValue,
        source: DATA_SOURCES_ENUM.SLC,
    };
};

export const getLastPathParameter = url => {
    if (typeof url !== 'string') return '';
    const cleanUrl = url.split('?')[0];
    return last(split(trimEnd(cleanUrl, '/'), '/')) || '';
};

export const isRequiredFieldValid = val => !isEmpty(trim(val));

export const getSelectStyles = (isErrorState = false) => ({
    control: (provided, state) => {
        let borderColor;
        if (isErrorState) {
            borderColor = COLOURS.RED;
        } else if (state.isFocused) {
            borderColor = COLOURS.PURPLE;
        } else {
            borderColor = provided.borderColor;
        }

        const boxShadow = state.isFocused
            ? `inset 0 0 0 1px ${borderColor}`
            : provided.boxShadow;

        return {
            ...provided,
            minHeight: '56px',
            borderRadius: '0',
            borderColor,
            boxShadow,
            transition: 'box-shadow 0.2s',
            '&:hover': {
                borderColor: !isErrorState && !state.isFocused && 'black',
            },
        };
    },
    placeholder: provided => ({
        ...provided,
        opacity: 0.7,
        color: isErrorState ? COLOURS.RED : provided.color,
    }),
});

export const snakeToTitleCase = str => startCase(toLower(str));

// SLC form validation schema.

const isCleanValueMeaningful = value => {
    if (typeof value !== 'string') return false;

    let cleaned = unidecode(value);
    cleaned = cleaned
        .replace(/[\n\r\t]/g, ' ') // Normalize whitespace characters.
        .replace(/[^\w\s]|_/g, '') // Remove all punctuation.
        .replace(/\s+/g, ' ') // Collapse multiple spaces.
        .trim() // Trim leading/trailing spaces.
        .toLowerCase();

    return cleaned.length > 0;
};

const slcTextFieldValidation = stringYup()
    .test(
        'is-trimmed',
        'Remove spaces at start and end of text.',
        value => value == null || value === value.trim(),
    )
    .test(
        'not-a-number',
        ({ label }) => `${label} cannot be a number.`,
        value => {
            if (value == null) return true;

            const numberPattern = /^-?(0|[1-9]\d*)(\.\d+)?$/;
            return !numberPattern.test(value);
        },
    )
    .test(
        'meaningful-characters',
        ({ label }) => `${label} cannot contain only spaces or symbols.`,
        value => value == null || isCleanValueMeaningful(value),
    )
    .max(
        SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH,
        ({ label }) =>
            `${label} cannot exceed ${SLC_FORM_CONSTRAINTS.MAX_STRING_LENGTH} characters.`,
    );

export const slcValidationSchema = objectYup({
    name: slcTextFieldValidation.required('Name is required.').label('Name'),
    address: slcTextFieldValidation
        .required('Address is required.')
        .label('Address'),
    country: objectYup().nullable().required('Country is required.'),
    productType: arrayYup().max(
        SLC_FORM_CONSTRAINTS.MAX_PRODUCT_TYPE_COUNT,
        `Maximum of ${SLC_FORM_CONSTRAINTS.MAX_PRODUCT_TYPE_COUNT} product types allowed.`,
    ),
    numberOfWorkers: stringYup()
        .test(
            'is-trimmed',
            'Remove spaces at start and end of entry.',
            value => value == null || value === value.trim(),
        )
        .test(
            'valid-format-and-range',
            'Enter a single positive number (e.g., 5) or a valid range ' +
                '(e.g., 3–10). In a range, the minimum value must be less ' +
                'than or equal to the maximum, and both must be at least 1.',
            value => {
                if (value == null) return true;

                const singleNumberPattern = /^\d+$/;
                const rangePattern = /^(\d+)-(\d+)$/;

                if (singleNumberPattern.test(value)) {
                    return !/^0/.test(value) && parseInt(value, 10) >= 1;
                }

                const match = value.match(rangePattern);
                if (match) {
                    const [minStr, maxStr] = match.slice(1, 3);

                    const min = parseInt(minStr, 10);
                    const max = parseInt(maxStr, 10);

                    if (/^0/.test(minStr) || /^0/.test(maxStr)) return false;

                    return min >= 1 && max >= 1 && min <= max;
                }

                return false;
            },
        ),
    parentCompany: slcTextFieldValidation.label('Parent company'),
});

/* eslint-disable camelcase */
export const formatExtendedField = ({
    value,
    field_name,
    created_at,
    contributor_name,
    is_from_claim,
    is_verified,
    formatValue = rawValue => rawValue,
}) => {
    const primary = renderUniqueListItems(formatValue(value), field_name);
    const secondary = formatAttribution(created_at, contributor_name);

    return {
        primary,
        secondary,
        embeddedSecondary: formatAttribution(created_at),
        isVerified: is_verified,
        isFromClaim: is_from_claim,
        key: uuidv4(),
    };
};

export const processDromoResults = (
    results,
    filename,
    fileInput,
    updateFileName,
) => {
    if (!results || results.length === 0) {
        return;
    }

    const headers = Object.keys(results[0]).join(',');
    const rows = results.map(row => Object.values(row).join(','));
    const csvContent = [headers, ...rows].join('\n');

    const csvBlob = new Blob([csvContent], { type: 'text/csv' });
    const csvFile = new File([csvBlob], filename.replace(/\.[^/.]+$/, '.csv'), {
        type: 'text/csv',
    });

    const inputEl = fileInput.current;
    if (inputEl) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(csvFile);
        inputEl.files = dataTransfer.files;

        updateFileName(fileInput);
    }
};
