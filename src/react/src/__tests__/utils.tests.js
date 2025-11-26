/* eslint-env jest */
/* eslint-disable no-useless-escape */

const mapValues = require('lodash/mapValues');
const isEqual = require('lodash/isEqual');
const includes = require('lodash/includes');
const turf = require('@turf/turf');

const {
    makeFacilityListsURL,
    makeSingleFacilityListURL,
    makeAPITokenURL,
    makeUserAPIInfoURL,
    makeGetContributorsURL,
    makeGetContributorTypesURL,
    makeGetCountriesURL,
    makeGetFacilitiesURL,
    makeGetFacilityByOSIdURL,
    makeClaimFacilityAPIURL,
    makeMergeTwoFacilitiesAPIURL,
    makeGetFacilitiesURLWithQueryString,
    getValueFromObject,
    createQueryStringFromSearchFilters,
    allFiltersAreEmpty,
    createFiltersFromQueryString,
    getValueFromEvent,
    getCheckedFromEvent,
    getFileFromInputRef,
    getFileNameFromInputRef,
    createSignupErrorMessages,
    createSignupRequestData,
    createProfileUpdateErrorMessages,
    createProfileUpdateRequestData,
    createErrorListFromResponseObject,
    mapDjangoChoiceTuplesToSelectOptions,
    allListsAreEmpty,
    makeFacilityDetailLink,
    makeFacilityClaimDetailsLink,
    getIDFromEvent,
    makeGetFacilityClaimByClaimIDURL,
    makeApproveFacilityClaimByClaimIDURL,
    makeDenyFacilityClaimByClaimIDURL,
    makeRevokeFacilityClaimByClaimIDURL,
    makeAddNewFacilityClaimReviewNoteURL,
    getBBoxForArrayOfGeoJSONPoints,
    makeFacilityListItemsDetailLink,
    makePaginatedFacilityListItemsDetailLinkWithRowCount,
    makeSliceArgumentsForTablePagination,
    getNumberFromParsedQueryStringParamOrUseDefault,
    createPaginationOptionsFromQueryString,
    createParamsFromQueryString,
    makeFeatureCollectionFromSingleFeature,
    createConfirmFacilityListItemMatchURL,
    createRejectFacilityListItemMatchURL,
    makeMyFacilitiesRoute,
    makeResetPasswordEmailURL,
    getTokenFromQueryString,
    makeResetPasswordConfirmURL,
    makeUserProfileURL,
    makeProfileRouteLink,
    joinDataIntoCSVString,
    updateListWithLabels,
    makeSubmitFormOnEnterKeyPressFunction,
    makeFacilityListItemsRetrieveCSVItemsURL,
    makeFacilityListDataURLs,
    makeFacilityListSummaryStatus,
    addProtocolToWebsiteURLIfMissing,
    convertFeatureFlagsObjectToListOfActiveFlags,
    checkWhetherUserHasDashboardAccess,
    claimAFacilityFormIsValid,
    claimFacilitySupportDocsIsValid,
    anyListItemMatchesAreInactive,
    pluralizeResultsCount,
    removeDuplicatesFromOtherLocationsData,
    makeGetSectorsURL,
    createUserDropdownLinks,
    createUploadFormErrorMessages,
    getLastPathParameter,
    generateRangeField,
    parseContribData,
    isRequiredFieldValid,
    getSelectStyles,
    getNumberOfWorkersValidationError,
    isValidNumberOfWorkers,
    snakeToTitleCase,
    slcValidationSchema,
    formatExtendedField,
    processDromoResults,
    formatPartnerFieldValue
} = require('../util/util');

const {
    OTHER,
    registrationFieldsEnum,
    registrationFormFields,
    profileFieldsEnum,
    profileFormFields,
    dashboardRoute,
    DEFAULT_PAGE,
    DEFAULT_ROWS_PER_PAGE,
    ENTER_KEY,
    facilityListItemStatusChoicesEnum,
    facilityListSummaryStatusMessages,
    FACILITIES_REQUEST_PAGE_SIZE,
    CLAIM_A_FACILITY,
    componentsWithErrorMessage,
} = require('../util/constants');

const COLOURS = require('../util/COLOURS').default;

it('gets correct error message component', () => {
    const correctListName = 'New & Test Name - Location, [Ltd].';
    const emptyListName = '';
    const listNameWithInvalidCharacters = 'Test / À location';
    const listNameWithOnlySymbolsAndNumbers = '53464&&&';
    const file = {
        current: {
            files: [
                'file',
            ],
        },
    };
    const noFile = undefined;

    const emptyListNameDataErrors = createUploadFormErrorMessages(emptyListName, file);
    const listNameWithInvalidCharactersDataErrors = createUploadFormErrorMessages(listNameWithInvalidCharacters, file);
    const listNameWithOnlySymbolsAndNumbersDataErrors = createUploadFormErrorMessages(listNameWithOnlySymbolsAndNumbers, file);
    const noFileDataErrors = createUploadFormErrorMessages(correctListName, noFile);
    const noDataErrors = createUploadFormErrorMessages(correctListName, file);

    expect(isEqual(emptyListNameDataErrors[0], componentsWithErrorMessage.missingListName)).toBe(true);
    expect(isEqual(listNameWithInvalidCharactersDataErrors[0], componentsWithErrorMessage.invalidCharacters)).toBe(true);
    expect(isEqual(listNameWithOnlySymbolsAndNumbersDataErrors[0], componentsWithErrorMessage.mustConsistOfLetters)).toBe(true);
    expect(isEqual(noFileDataErrors[0], componentsWithErrorMessage.missingFile)).toBe(true);
    expect(isEqual(noDataErrors.length, 0)).toBe(true);
});

it('creates a route for checking facility list items', () => {
    const listID = 'hello';
    const expectedRoute = '/lists/hello';
    expect(makeFacilityListItemsDetailLink(listID)).toBe(expectedRoute);
});

it('creates a paginated facility list items route with the row count', () => {
    const listID = 'foo';
    const page = 'bar';
    const rowCount = 'baz';
    const expectedRoute = '/lists/foo?page=bar&rowsPerPage=baz';
    expect(makePaginatedFacilityListItemsDetailLinkWithRowCount(listID, page, rowCount))
        .toBe(expectedRoute);
});

it('creates API URLs for a user\'s facility lists viewset', () => {
    const facilityListsURL = '/api/facility-lists/';
    expect(makeFacilityListsURL()).toEqual(facilityListsURL);
    const singleFacilityListURL = '/api/facility-lists/2/';
    expect(makeSingleFacilityListURL(2)).toEqual(singleFacilityListURL);
});

it('creates an API URL for generating an API token', () => {
    const uid = 123;
    const expectedMatch = '/api-token-auth/';
    expect(makeAPITokenURL(uid)).toEqual(expectedMatch);
});

it('creates an API URL for getting contributor API information', () => {
    const uid = 123;
    const expectedMatch = `/user-api-info/${uid}/`;
    expect(makeUserAPIInfoURL(uid)).toEqual(expectedMatch);
});

it('creates API URLs for getting contributor, contributor type, country, and sector options', () => {
    const contributorMatch = '/api/contributors/';
    const contributorTypesMatch = '/api/contributor-types/';
    const countriesMatch = '/api/countries/';
    const sectorsMatch = '/api/sectors/';

    expect(makeGetContributorsURL()).toEqual(contributorMatch);
    expect(makeGetContributorTypesURL()).toEqual(contributorTypesMatch);
    expect(makeGetCountriesURL()).toEqual(countriesMatch);
    expect(makeGetSectorsURL()).toEqual(sectorsMatch);
});

it('creates an API URL for getting all facilities', () => {
    const expectedMatch = '/api/facilities/';
    expect(makeGetFacilitiesURL()).toEqual(expectedMatch);
});

it('creates an API URL for getting a single facility by OS ID', () => {
    const expectedMatch = '/api/facilities/12345/?created_at_of_data_points=false&pending_claim_info=true';
    expect(makeGetFacilityByOSIdURL(12345)).toEqual(expectedMatch);
});

it('creates an API URL for getting facilities with a query string', () => {
    const qs = 'hello=world';
    const expectedMatch = `/api/facilities/?hello=world&number_of_public_contributors=true&pageSize=${FACILITIES_REQUEST_PAGE_SIZE}`;
    expect(makeGetFacilitiesURLWithQueryString(qs, FACILITIES_REQUEST_PAGE_SIZE))
        .toEqual(expectedMatch);
});

it('gets the value from a React Select option object', () => {
    const reactSelectOption = { value: 'value' };
    const expectedMatch = 'value';
    expect(getValueFromObject(reactSelectOption)).toEqual(expectedMatch);
});

it('creates a querystring from a set of filter selection', () => {
    const emptyFilterSelections = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: []
    };

    const expectedEmptySelectionQSMatch = '';
    expect(createQueryStringFromSearchFilters(emptyFilterSelections))
        .toEqual(expectedEmptySelectionQSMatch);

    const multipleFilterSelections = {
        facilityFreeTextQuery: '',
        contributors: [
            { value: 'foo', label: 'foo' },
            { value: 'bar', label: 'bar' },
            { value: 'baz', label: 'bar' },
        ],
        contributorTypes: [],
        countries: [
            { value: 'country', label: 'country' },
        ],
        sectors: [
            { value: 'Apparel', label: 'Apparel' },
            { value: 'Mining', label: 'Mining' },
        ],
    };

    const expectedMultipleFilterSelectionsMatch =
        'contributors=bar&contributors=baz&contributors=foo&countries=country'
            .concat('&sectors=Apparel&sectors=Mining');
    expect(createQueryStringFromSearchFilters(multipleFilterSelections))
        .toEqual(expectedMultipleFilterSelectionsMatch);

    const allFilters = {
        facilityFreeTextQuery: 'hello',
        contributors: [
            { value: 'hello', label: 'hello' },
            { value: 'world', label: 'hello' },
        ],
        contributorTypes: [
            { value: 'foo', label: 'foo' },
        ],
        countries: [
            { value: 'bar', label: 'bar' },
        ],
        sectors: [
            { value: 'baz', label: 'baz' },
        ],
    };

    const expectedAllFiltersMatch =
        'q=hello&contributors=hello&contributors=world'
            .concat('&contributor_types=foo&countries=bar&sectors=baz');
    expect(createQueryStringFromSearchFilters(allFilters))
        .toEqual(expectedAllFiltersMatch);
});

it('checks whether the filters object has only empty values', () => {
    const emptyFilters = {
        hello: '',
        world: [],
        foo: {},
        bar: null,
    };

    expect(allFiltersAreEmpty(emptyFilters)).toBe(true);

    const nonEmptyFilters = {
        foo: '',
        bar: [],
        baz: [1],
    };

    expect(allFiltersAreEmpty(nonEmptyFilters)).toBe(false);

    const nonEmptyStringFilter = {
        hello: 'hello',
        world: [],
    };

    expect(allFiltersAreEmpty(nonEmptyStringFilter)).toBe(false);
});

it('creates a set of filters from a querystring', () => {
    const contributorsString = '?contributors=1&contributors=2';
    const expectedContributorsMatch = {
        facilityFreeTextQuery: '',
        contributors: [
            {
                value: 1,
                label: '1',
            },
            {
                value: 2,
                label: '2',
            },
        ],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
        }
    };

    expect(
        createFiltersFromQueryString(contributorsString),
    ).toEqual(expectedContributorsMatch);

    const combinedContributorsString = '?contributors=1&contributors=2&combine_contributors=AND';
    const expectedCombinedContributorsMatch = {
        facilityFreeTextQuery: '',
        contributors: [
            {
                value: 1,
                label: '1',
            },
            {
                value: 2,
                label: '2',
            },
        ],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: 'AND',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(combinedContributorsString),
    ).toEqual(expectedCombinedContributorsMatch);

    const defaultSortingString = '?sort_by=name_asc';
    const expectedSortingMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(defaultSortingString),
    ).toEqual(expectedSortingMatch);

    const listsString = '?contributors=1&lists=2';
    const expectedListsMatch = {
        facilityFreeTextQuery: '',
        contributors: [
            {
                value: 1,
                label: '1',
            },
        ],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [
            {
                value: 2,
                label: '2',
            },
        ],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(listsString),
    ).toEqual(expectedListsMatch);

    const typesString = '?contributor_types=Union&contributor_types=Service Provider';
    const expectedTypesMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [
            {
                value: 'Union',
                label: 'Union',
            },
            {
                value: 'Service Provider',
                label: 'Service Provider',
            },
        ],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(typesString),
    ).toEqual(expectedTypesMatch);

    const countriesString = '?countries=US&countries=CN';
    const expectedCountriesMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [
            {
                value: 'US',
                label: 'US',
            },
            {
                value: 'CN',
                label: 'CN',
            },
        ],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(countriesString),
    ).toEqual(expectedCountriesMatch);

    const stringWithCountriesMissing = '?contributor_types=Union&countries=';
    const expectedMissingCountriesMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [
            {
                value: 'Union',
                label: 'Union',
            },
        ],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(stringWithCountriesMissing),
    ).toEqual(expectedMissingCountriesMatch);

    const parentCompanyString = '?parent_company=1&parent_company=Test Company'
    const expectedParentCompanyMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [{
            value: 1,
            label: '1',
        },
        {
            value: 'Test Company',
            label: 'Test Company',
        }],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(parentCompanyString),
    ).toEqual(expectedParentCompanyMatch);

    const facilityTypeString = '?facility_type=Final Product Assembly&facility_type=Office / HQ'
    const expectedFacilityTypeMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [{
            value: 'Final Product Assembly',
            label: 'Final Product Assembly',
        },
        {
            value: 'Office / HQ',
            label: 'Office / HQ',
        }],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(facilityTypeString),
    ).toEqual(expectedFacilityTypeMatch);

    const processingTypeString = '?processing_type=Batch Dyeing&processing_type=Embellishment'
    const expectedProcessingTypeMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [{
            value: 'Batch Dyeing',
            label: 'Batch Dyeing',
        },
        {
            value: 'Embellishment',
            label: 'Embellishment',
        }],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(processingTypeString),
    ).toEqual(expectedProcessingTypeMatch);

    const productTypeString = '?product_type=Beauty&product_type=Jackets/Blazers'
    const expectedProductTypeMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [{
            value: 'Beauty',
            label: 'Beauty',
        },
        {
            value: 'Jackets/Blazers',
            label: 'Jackets/Blazers',
        }],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(productTypeString),
    ).toEqual(expectedProductTypeMatch);

    const numberofWorkersString = '?number_of_workers=Less than 1000&number_of_workers=1001-5000'
    const expectedNumberOfWorkersMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [{
            value: 'Less than 1000',
            label: 'Less than 1000',
        },
        {
            value: '1001-5000',
            label: '1001-5000',
        }],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(numberofWorkersString),
    ).toEqual(expectedNumberOfWorkersMatch);

    const nativeLanguageNameString = '?native_language_name=杭州'
    const expectedNativeLanguageNameMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '杭州',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(nativeLanguageNameString),
    ).toEqual(expectedNativeLanguageNameMatch);

    const claimStatusesString = '?statuses=PENDING&statuses=APPROVED&statuses=DENIED&statuses=REVOKED'
    const expectedClaimStatusesMatch = {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        sectors: [],
        statuses: [
            {
                "label": "PENDING",
                "value": "PENDING",
            },
            {
                "label": "APPROVED",
                "value": "APPROVED",
            },
            {
                "label": "DENIED",
                "value": "DENIED",
            },
            {
                "label": "REVOKED",
                "value": "REVOKED",
            },
        ],
        lists: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        sortAlgorithm: {
            value: 'name_asc', label: 'A to Z',
          }
    };

    expect(
        createFiltersFromQueryString(claimStatusesString),
    ).toEqual(expectedClaimStatusesMatch);
});

it('creates a facility detail link', () => {
    const expectedMatch = '/facilities/hello';
    const link = makeFacilityDetailLink('hello');

    expect(link).toEqual(expectedMatch);
});

it('gets the value from an event on a DOM input', () => {
    const value = 'value';
    const mockEvent = {
        target: {
            value,
        },
    };

    expect(getValueFromEvent(mockEvent)).toEqual(value);
});

it('gets the checked state from an event on a DOM checkbox input', () => {
    const checked = true;
    const mockEvent = {
        target: {
            checked,
        },
    };

    expect(getCheckedFromEvent(mockEvent)).toEqual(true);
});

it('gets the file from a file input ref', () => {
    const file = {
        current: {
            files: [
                'file',
            ],
        },
    };

    expect(getFileFromInputRef(file)).toEqual('file');
});

it('gets null from an empty file input ref', () => {
    const file = undefined;

    expect(getFileFromInputRef(file)).toEqual(null);
});

it('gets the filename from a file input ref', () => {
    const file = {
        current: {
            files: [
                {
                    name: 'file',
                },
            ],
        },
    };

    expect(getFileNameFromInputRef(file))
        .toEqual('file');
});

it('gets an empty string for the filename from an empty file input ref', () => {
    const file = undefined;

    expect(getFileNameFromInputRef(file))
        .toEqual('');
});

it('creates a list of error messages if any required signup or profile update fields are missing', () => {
    const incompleteSignupForm = mapValues(registrationFieldsEnum, '');

    const expectedSignupErrorMessageCount = registrationFormFields
        .filter(({ required }) => required)
        .filter(({ id }) => id !== registrationFieldsEnum.otherContributorType)
        .length;

    expect(createSignupErrorMessages(incompleteSignupForm).length)
        .toEqual(expectedSignupErrorMessageCount);

    const incompleteProfileForm = mapValues(profileFieldsEnum, '');

    const expectedProfileErrorMessageCount = profileFormFields
        .filter(({ required }) => required)
        .filter(({ id }) => id !== registrationFieldsEnum.otherContributorType)
        .length;

    expect(createProfileUpdateErrorMessages(incompleteProfileForm).length)
        .toEqual(expectedProfileErrorMessageCount);
});

it('creates zero error messages if all required signup or profile update fields are present', () => {
    const completeSignupForm = registrationFieldsEnum;

    expect(createSignupErrorMessages(completeSignupForm).length)
        .toEqual(0);

    const completeProfileForm = profileFieldsEnum;

    expect(createProfileUpdateErrorMessages(completeProfileForm).length)
        .toEqual(0);
});

it('creates an error message for missing otherContributorType field when it is required', () => {
    const completeSignupForm = Object.assign({}, registrationFieldsEnum, {
        [registrationFieldsEnum.contributorType]: OTHER,
        [registrationFieldsEnum.otherContributorType]: '',
    });

    expect(createSignupErrorMessages(completeSignupForm).length)
        .toEqual(1);

    const completeProfileForm = Object.assign({}, profileFieldsEnum, {
        [registrationFieldsEnum.contributorType]: OTHER,
        [registrationFieldsEnum.otherContributorType]: '',
    });

    expect(createProfileUpdateErrorMessages(completeProfileForm).length)
        .toEqual(1);
});

it('creates no error message for missing otherContributorType field when present', () => {
    const completeSignupForm = Object.assign({}, registrationFieldsEnum, {
        [registrationFieldsEnum.contributorType]: OTHER,
        [registrationFieldsEnum.otherContributorType]: 'other contributor type',
    });

    expect(createSignupErrorMessages(completeSignupForm).length)
        .toEqual(0);

    const completeProfileForm = Object.assign({}, profileFieldsEnum, {
        [registrationFieldsEnum.contributorType]: OTHER,
        [registrationFieldsEnum.otherContributorType]: 'other contributor type',
    });

    expect(createProfileUpdateErrorMessages(completeProfileForm).length)
        .toEqual(0);
});

it('correctly reformats data to send to Django from the signup form state', () => {
    // drop `confirmPassword` since it's sent as `password` to Django
    const {
        confirmPassword,
        ...completeForm
    } = registrationFieldsEnum;

    const signupRequestData = createSignupRequestData(completeForm);

    registrationFormFields.forEach(({ id, modelFieldName }) =>
        expect(signupRequestData[modelFieldName]).toEqual(completeForm[id]));

    const profileRequestData = createProfileUpdateRequestData(profileFieldsEnum);

    profileFormFields.forEach(({ id, modelFieldName }) =>
        expect(profileRequestData[modelFieldName]).toEqual(profileFieldsEnum[id]));
});

it('creates a list of field errors from a Django error object', () => {
    const djangoErrors = {
        email: [
            'this email is already used',
        ],
        name: [
            'this name has too few characters',
            'this name has too few vowels',
        ],
    };

    const expectedErrorMessages = [
        'email: this email is already used',
        'name: this name has too few characters',
        'name: this name has too few vowels',
    ];

    const errorMessages = createErrorListFromResponseObject(djangoErrors);

    expect(errorMessages).toEqual(expectedErrorMessages);
});

it('correctly maps a list of Choice tuples from Django into an array of select options', () => {
    const expectedOptions = [
        {
            value: 'one',
            label: 'one',
        },
        {
            value: 'two',
            label: 'two',
        },
    ];

    const mockChoices = [['one', 'one'], ['two', 'two']];

    const optionsFromChoices = mapDjangoChoiceTuplesToSelectOptions(mockChoices);

    expect(isEqual(expectedOptions, optionsFromChoices)).toBe(true);
});

it('correctly checks whether an array of arrays contains only empty arrays', () => {
    const fourEmptyLists = [[], [], [], []];
    const zeroEmptyLists = [];
    const oneEmptyList = [[]];

    expect(allListsAreEmpty(...fourEmptyLists)).toBe(true);
    expect(allListsAreEmpty(...zeroEmptyLists)).toBe(true);
    expect(allListsAreEmpty(...oneEmptyList)).toBe(true);

    const oneNonEmptyList = [['hello']];
    const threeEmptyListsOneNonEmptyList = [[], [], [], [{ hello: 'world' }]];
    const sixNonEmptyLists = [
        ['hello'],
        [
            { hello: 'hello' },
            { world: 'world' },
        ],
        [1, 2, 3, 4, 5],
        [isEqual],
        [new Set([1, 2, 3, 4])],
        [new Map([['hello', 'hello'], ['world', 'world']])],
    ];

    expect(allListsAreEmpty(...oneNonEmptyList)).toBe(false);
    expect(allListsAreEmpty(...threeEmptyListsOneNonEmptyList)).toBe(false);
    expect(allListsAreEmpty(...sixNonEmptyLists)).toBe(false);
});

it('creates a bounding box for an array of GeoJSON points', () => {
    const inputData = [
        turf.point([0, 1]),
        turf.point([1, 0]),
    ];

    const expectedResult = [
        0,
        0,
        1,
        1,
    ];

    expect(getBBoxForArrayOfGeoJSONPoints(inputData)).toEqual(expectedResult);
});

it('creates arguments for slicing a list of items for paginating', () => {
    const pageZero = 0;
    const pageOne = 1;
    const pageSeven = 7;
    const twentyRows = 20;
    const twentyFiveRows = 25;

    const expectedPageZeroTwentyRowsMatch = [
        0,
        20,
    ];

    expect(isEqual(
        makeSliceArgumentsForTablePagination(pageZero, twentyRows),
        expectedPageZeroTwentyRowsMatch,
    )).toBe(true);

    const expectedPageOneTwentyRowsMatch = [
        20,
        40,
    ];

    expect(isEqual(
        makeSliceArgumentsForTablePagination(pageOne, twentyRows),
        expectedPageOneTwentyRowsMatch,
    )).toBe(true);

    const expectedPageOneTwentyFiveRowsMatch = [
        25,
        50,
    ];

    expect(isEqual(
        makeSliceArgumentsForTablePagination(pageOne, twentyFiveRows),
        expectedPageOneTwentyFiveRowsMatch,
    )).toBe(true);

    const expectedPageSevenTwentyFiveRowsMatch = [
        175,
        200,
    ];

    expect(isEqual(
        makeSliceArgumentsForTablePagination(pageSeven, twentyFiveRows),
        expectedPageSevenTwentyFiveRowsMatch,
    )).toBe(true);
});

it('gets a number from a parsed querystring param or uses the default', () => {
    const defaultValue = 12345;
    const arrayOfStrings = [
        'hello',
        'world',
    ];

    expect(getNumberFromParsedQueryStringParamOrUseDefault(arrayOfStrings, defaultValue))
        .toBe(defaultValue);

    const firstNumber = 5;
    const arrayOfNumbers = [
        firstNumber,
        10,
        20,
    ];

    expect(getNumberFromParsedQueryStringParamOrUseDefault(arrayOfNumbers, defaultValue))
        .toBe(firstNumber);

    const fiveString = '5';

    expect(getNumberFromParsedQueryStringParamOrUseDefault(fiveString, defaultValue))
        .toBe(firstNumber);

    const stringValue = 'hello';
    expect(getNumberFromParsedQueryStringParamOrUseDefault(stringValue, defaultValue))
        .toBe(defaultValue);
});

it('creates a set of pagination options from a querystring', () => {
    const emptyQueryString = '';
    const expectedPaginationValuesForEmptyQueryString = {
        page: DEFAULT_PAGE,
        rowsPerPage: DEFAULT_ROWS_PER_PAGE,
    };

    expect(isEqual(
        createPaginationOptionsFromQueryString(emptyQueryString),
        expectedPaginationValuesForEmptyQueryString,
    )).toBe(true);

    const pageOnlyQueryString = '?page=1000';
    const expectedValuesForPageOnlyQueryString = {
        page: 1000,
        rowsPerPage: DEFAULT_ROWS_PER_PAGE,
    };

    expect(isEqual(
        createPaginationOptionsFromQueryString(pageOnlyQueryString),
        expectedValuesForPageOnlyQueryString,
    )).toBe(true);

    const pageRowQueryString = '?page=500&rowsPerPage=12345';
    const expectedPageRowValues = {
        page: 500,
        rowsPerPage: 12345,
    };

    expect(isEqual(
        createPaginationOptionsFromQueryString(pageRowQueryString),
        expectedPageRowValues,
    )).toBe(true);

    const complexQueryString = '?page=hello&page=world&rowsPerPage=hello';
    const expectedComplexQueryStringValues = {
        page: DEFAULT_PAGE,
        rowsPerPage: DEFAULT_ROWS_PER_PAGE,
    };

    expect(isEqual(
        createPaginationOptionsFromQueryString(complexQueryString),
        expectedComplexQueryStringValues,
    )).toBe(true);
});

it('creates params from a query string', () => {
    const emptyQueryString = '';
    const expectedParamsForEmptyQueryString = {};
    expect(createParamsFromQueryString(emptyQueryString))
        .toEqual(expectedParamsForEmptyQueryString);

    const oneStatusQueryString = '?status=NEW_FACILITY';
    const expectedParamsForOneStatus = { status: ['NEW_FACILITY'] };
    expect(createParamsFromQueryString(oneStatusQueryString))
        .toEqual(expectedParamsForOneStatus);

    const twoStatusQueryString = '?status=NEW_FACILITY&status=MATCHED';
    const expectedParamsForTwoStatus = { status: ['NEW_FACILITY', 'MATCHED'] };
    expect(createParamsFromQueryString(twoStatusQueryString))
        .toEqual(expectedParamsForTwoStatus);

    const ignoredArgQueryString = '?foo=bar';
    const expectedParamsForIgnoredArg = {};
    expect(createParamsFromQueryString(ignoredArgQueryString))
        .toEqual(expectedParamsForIgnoredArg);
});

it('creates a geojson FeatureCollection from a single geojson Feature', () => {
    const feature = {
        id: 1,
        type: 'Feature',
        geometry: 'geometry',
        properties: {
            hello: 'world',
        },
    };

    const expectedFeatureCollection = {
        type: 'FeatureCollection',
        features: [
            {
                id: 1,
                type: 'Feature',
                geometry: 'geometry',
                properties: {
                    hello: 'world',
                },
            },
        ],
    };

    expect(isEqual(
        makeFeatureCollectionFromSingleFeature(feature),
        expectedFeatureCollection,
    )).toBe(true);
});

it('creates URLs for confirming or rejecting a facility list item match', () => {
    const matchId = 'matchid';
    const expectedConfirmURL = '/api/facility-matches/matchid/confirm/';
    const expectedRejectURL = '/api/facility-matches/matchid/reject/';

    expect(createConfirmFacilityListItemMatchURL(matchId)).toBe(expectedConfirmURL);
    expect(createRejectFacilityListItemMatchURL(matchId)).toBe(expectedRejectURL);
});

it('creates a link to see facilities for a contributor ID', () => {
    const contributor = 'contributor';
    const expectedFacilitiesRoute = '/facilities/?contributors=contributor';

    expect(makeMyFacilitiesRoute(contributor)).toBe(expectedFacilitiesRoute);
});

it('creates a URL for requesting a password reset', () => {
    const expectedURL = '/rest-auth/password/reset/';
    expect(makeResetPasswordEmailURL()).toBe(expectedURL);
});

it('creates a URL for confirming a password reset', () => {
    const expectedURL = '/rest-auth/password/reset/confirm/';
    expect(makeResetPasswordConfirmURL()).toBe(expectedURL);
});

it('creates a URL for retrieving a user profile', () => {
    const userID = 'userID';
    const expectedURL = '/user-profile/userID/';
    expect(makeUserProfileURL(userID)).toBe(expectedURL);
});

it('creates a route link for viewing a user profile', () => {
    const userID = 'userID';
    const expectedRoute = '/profile/userID';
    expect(makeProfileRouteLink(userID)).toBe(expectedRoute);
});

it('gets a `token` from a querystring', () => {
    const simpleToken = '?token=helloworld';
    const expectedSimpleTokenMatch = 'helloworld';

    expect(getTokenFromQueryString(simpleToken)).toBe(expectedSimpleTokenMatch);

    const missingToken = '?hello=world';
    const expectedMissingTokenMatch = '';

    expect(getTokenFromQueryString(missingToken)).toBe(expectedMissingTokenMatch);

    const listOfTokens = '?token=foo&token=bar&token=baz';
    const expectedListOfTokensMatch = 'foo';

    expect(getTokenFromQueryString(listOfTokens)).toBe(expectedListOfTokensMatch);

    const missingQueryString = '';
    const expectedMissingQueryStringMatch = '';

    expect(getTokenFromQueryString(missingQueryString)).toBe(expectedMissingQueryStringMatch);
});

it('joins a 2-d array into a correctly escaped CSV string', () => {
    const numericArray = [
        [
            1,
            2,
        ],
        [
            3,
            4,
        ],
    ];
    const expectedNumericArrayMatch = '1,2\n3,4\n';
    expect(joinDataIntoCSVString(numericArray)).toBe(expectedNumericArrayMatch);

    const stringArray = [
        [
            'hello',
            'world',
        ],
        [
            'foo',
            '13e65088',
        ],
    ];
    const expectedStringArrayMatch = '"hello","world"\n"foo","13e65088"\n';
    expect(joinDataIntoCSVString(stringArray)).toBe(expectedStringArrayMatch);

    const mixedArray = [
        [
            1,
            'hello',
        ],
        [
            2,
            'world',
        ],
    ];
    const expectedMixedArrayMatch = '1,"hello"\n2,"world"\n';
    expect(joinDataIntoCSVString(mixedArray)).toBe(expectedMixedArrayMatch);

    const escapedArray = [
        [
            'foo, bar, baz',
            'hello "world"',
        ],
        [
            'foo, "bar", baz',
            'hello,\nworld',
        ],
    ];
    const expectedEscapedArrayMatch =
        '"foo, bar, baz","hello ""world"""\n"foo, ""bar"", baz","hello, world"\n';
    expect(joinDataIntoCSVString(escapedArray)).toBe(expectedEscapedArrayMatch);
});

it('updates a list of unlabeled values with the correct labels from a given source', () => {
    const source = [
        {
            value: 67,
            label: 'Aguilar, Stanley and Lewis',
        },
        {
            value: 57,
            label: 'Alvarez PLC',
        },
        {
            value: 14,
            label: 'Arnold-Adams',
        },
    ];
    const unlabeled = [
        {
            value: 57,
            label: '57', // Unlabeled, should be corrected
        },
        {
            value: 14,
            label: 'XYZ', // Mislabaled, should be corrected
        },
        {
            value: 89,
            label: 'ABC', // Does not exist in source, should be dropped
        },
    ];

    const corrected = [
        {
            value: 57,
            label: 'Alvarez PLC',
        },
        {
            value: 14,
            label: 'Arnold-Adams',
        },
    ];

    expect(isEqual(
        updateListWithLabels(unlabeled, source),
        corrected,
    )).toBe(true);
});

it('calls a given function when the enter key has been pressed in a form input', () => {
    const dispatchSubmitForm = jest.fn();

    const enterKeyPressHandler = makeSubmitFormOnEnterKeyPressFunction(dispatchSubmitForm);

    const keyPressEvent = {
        key: ENTER_KEY,
    };

    enterKeyPressHandler(keyPressEvent);
    expect(dispatchSubmitForm).toHaveBeenCalled();
});

it('does not call a given function when a non-enter key has been pressed in a form input', () => {
    const dispatchSubmitForm = jest.fn();

    const enterKeyPressHandler = makeSubmitFormOnEnterKeyPressFunction(dispatchSubmitForm);

    const keyPressEvent = {
        key: 'a',
    };

    enterKeyPressHandler(keyPressEvent);
    expect(dispatchSubmitForm).not.toHaveBeenCalled();
});

it('makes a link for retrieving a page of facility list items for downloading a CSV', () => {
    const listID = 10;
    const page = 5;

    const expectedURL = '/api/facility-lists/10/items/?page=5&pageSize=100';

    expect(makeFacilityListItemsRetrieveCSVItemsURL(listID, page))
        .toBe(expectedURL);
});

it('creates a list of data URLs for retrieving facility list items data', () => {
    const listID = 17;
    const count = 1385;

    const expectedURLs = [
        '/api/facility-lists/17/items/?page=1&pageSize=100',
        '/api/facility-lists/17/items/?page=2&pageSize=100',
        '/api/facility-lists/17/items/?page=3&pageSize=100',
        '/api/facility-lists/17/items/?page=4&pageSize=100',
        '/api/facility-lists/17/items/?page=5&pageSize=100',
        '/api/facility-lists/17/items/?page=6&pageSize=100',
        '/api/facility-lists/17/items/?page=7&pageSize=100',
        '/api/facility-lists/17/items/?page=8&pageSize=100',
        '/api/facility-lists/17/items/?page=9&pageSize=100',
        '/api/facility-lists/17/items/?page=10&pageSize=100',
        '/api/facility-lists/17/items/?page=11&pageSize=100',
        '/api/facility-lists/17/items/?page=12&pageSize=100',
        '/api/facility-lists/17/items/?page=13&pageSize=100',
        '/api/facility-lists/17/items/?page=14&pageSize=100',
    ];

    expect(isEqual(
        makeFacilityListDataURLs(listID, count),
        expectedURLs,
    )).toBe(true);

    const smallerListID = 14;
    const smallerListCount = 25;

    const smallerExpectedURLs = [
        '/api/facility-lists/14/items/?page=1&pageSize=100',
    ];

    expect(isEqual(
        makeFacilityListDataURLs(smallerListID, smallerListCount),
        smallerExpectedURLs,
    )).toBe(true);
});

it('creates a summary status message given a list of facility list item statuses', () => {
    expect(isEqual(
        makeFacilityListSummaryStatus([
            facilityListItemStatusChoicesEnum.UPLOADED,
            facilityListItemStatusChoicesEnum.GEOCODED,
            facilityListItemStatusChoicesEnum.ERROR_GEOCODING,
        ]),
        `${facilityListSummaryStatusMessages.PROCESSING} ${facilityListSummaryStatusMessages.ERROR}`,
    )).toBe(true);

    expect(isEqual(
        makeFacilityListSummaryStatus([
            facilityListItemStatusChoicesEnum.UPLOADED,
            facilityListItemStatusChoicesEnum.GEOCODED,
        ]),
        `${facilityListSummaryStatusMessages.PROCESSING}`,
    )).toBe(true);

    expect(isEqual(
        makeFacilityListSummaryStatus([
            facilityListItemStatusChoicesEnum.POTENTIAL_MATCH,
            facilityListItemStatusChoicesEnum.ERROR_MATCHING,
        ]),
        `${facilityListSummaryStatusMessages.AWAITING} ${facilityListSummaryStatusMessages.ERROR}`,
    )).toBe(true);

    expect(isEqual(
        makeFacilityListSummaryStatus([
            facilityListItemStatusChoicesEnum.CONFIRMED_MATCH,
            facilityListItemStatusChoicesEnum.MATCHED,
        ]),
        `${facilityListSummaryStatusMessages.COMPLETED}`,
    )).toBe(true);

    expect(isEqual(
        makeFacilityListSummaryStatus([
            facilityListItemStatusChoicesEnum.CONFIRMED_MATCH,
            facilityListItemStatusChoicesEnum.MATCHED,
            facilityListItemStatusChoicesEnum.ERROR,
        ]),
        `${facilityListSummaryStatusMessages.ERROR}`,
    )).toBe(true);

    expect(isEqual(
        makeFacilityListSummaryStatus([
            facilityListItemStatusChoicesEnum.POTENTIAL_MATCH,
            facilityListItemStatusChoicesEnum.CONFIRMED_MATCH,
            facilityListItemStatusChoicesEnum.MATCHED,
            facilityListItemStatusChoicesEnum.ERROR,
        ]),
        `${facilityListSummaryStatusMessages.AWAITING} ${facilityListSummaryStatusMessages.ERROR}`,
    )).toBe(true);
});

it('adds a protocol to a website URL if the protocol is missing, but not if it is there', () => {
    const urlWithHTTP = 'http://example.com';
    const expectedResultForURLWithHTTP = 'http://example.com';

    expect(addProtocolToWebsiteURLIfMissing(urlWithHTTP))
        .toBe(expectedResultForURLWithHTTP);

    const urlWithHTTPS = 'https://example.com';
    const expectedResultForURLWithHTTPS = 'https://example.com';

    expect(addProtocolToWebsiteURLIfMissing(urlWithHTTPS))
        .toBe(expectedResultForURLWithHTTPS);

    const urlWithNoProtocol = 'example.com';
    const expectedResultForURLWithNoProtocol = 'http://example.com';

    expect(addProtocolToWebsiteURLIfMissing(urlWithNoProtocol))
        .toBe(expectedResultForURLWithNoProtocol);
});

it('creates a list including only active features from a feature flags object', () => {
    const IMPORT_SHAPEFILE = 'import_shapefile';
    const EXPORT_SHAPEFILE = 'export_shapefile';

    const features = {
        import_shapefile: false,
        export_shapefile: true,
    };

    const listOfActiveFeatureFlags = convertFeatureFlagsObjectToListOfActiveFlags(features);

    expect(includes(listOfActiveFeatureFlags, IMPORT_SHAPEFILE))
        .toBe(false);

    expect(includes(listOfActiveFeatureFlags, EXPORT_SHAPEFILE))
        .toBe(true);
});

it('checks whether a user has dashboard access', () => {
    const authorizedUser = {
        is_superuser: true,
    };

    const unauthorizedUser = {
        is_superuser: false,
    };

    expect(checkWhetherUserHasDashboardAccess(authorizedUser))
        .toBe(true);

    expect(checkWhetherUserHasDashboardAccess(unauthorizedUser))
        .toBe(false);
});

it('creates a URL for POSTing the claim a facility form', () => {
    const osID = '12345';

    const expectedURLMatch = '/api/facilities/12345/claim/';

    expect(isEqual(
        makeClaimFacilityAPIURL(osID),
        expectedURLMatch,
    )).toBe(true);
});

it('checks whether the claim a facility form is valid', () => {
    const validForm = {
        yourName: 'Name',
        yourTitle: 'Person',
        yourBusinessWebsite: 'www.example.com',
        businessWebsite: 'www.example.com',
        businessLinkedinProfile: 'www.example.com',
        businessUploadFiles: [],
    };

    expect(isEqual(
        claimAFacilityFormIsValid(validForm),
        true,
    )).toBe(true);

    expect(isEqual(
        claimFacilitySupportDocsIsValid(validForm),
        true,
    )).toBe(true);

    const invalidForm = {
        yourTitle: 'Person',
        yourBusinessWebsite: 'www.example.com',
        businessWebsite: 'www.example.com',
        businessLinkedinProfile: 'www.example.com',
        businessUploadFiles: [],
    };

    expect(isEqual(
        claimAFacilityFormIsValid(invalidForm),
        true,
    )).toBe(false);

    expect(isEqual(
        claimFacilitySupportDocsIsValid(invalidForm),
        true,
    )).toBe(false);
});

it('creates a facility claim details link', () => {
    const claimID = 'claimID';
    const expectedMatch = '/dashboard/claims/claimID';

    expect(isEqual(
        makeFacilityClaimDetailsLink(claimID),
        expectedMatch,
    )).toBe(true);
});

it('gets an ID from an event', () => {
    const event = {
        target: {
            id: 'id',
        },
    };

    const expectedID = 'id';

    expect(isEqual(
        getIDFromEvent(event),
        expectedID,
    )).toBe(true);
});

it('creates links to get facility claim details from a claim ID', () => {
    const claimID = 'claimID';
    const expectedMatch = '/api/facility-claims/claimID/';

    expect(isEqual(
        expectedMatch,
        makeGetFacilityClaimByClaimIDURL(claimID),
    )).toBe(true);

    const expectedApproveMatch = '/api/facility-claims/claimID/approve/';
    const expectedDenyMatch = '/api/facility-claims/claimID/deny/';
    const expectedRevokeMatch = '/api/facility-claims/claimID/revoke/';
    const expectedAddNoteMatch = '/api/facility-claims/claimID/note/';

    expect(isEqual(
        expectedApproveMatch,
        makeApproveFacilityClaimByClaimIDURL(claimID),
    )).toBe(true);

    expect(isEqual(
        expectedDenyMatch,
        makeDenyFacilityClaimByClaimIDURL(claimID),
    )).toBe(true);

    expect(isEqual(
        expectedRevokeMatch,
        makeRevokeFacilityClaimByClaimIDURL(claimID),
    )).toBe(true);

    expect(isEqual(
        expectedAddNoteMatch,
        makeAddNewFacilityClaimReviewNoteURL(claimID),
    )).toBe(true);
});

it('creates an API URL for merging two facilties', () => {
    const targetID = 'targetID';
    const toMergeID = 'toMergeID';

    const expectedURL =
        '/api/facilities/merge/?target=targetID&merge=toMergeID';

    expect(isEqual(
        expectedURL,
        makeMergeTwoFacilitiesAPIURL(targetID, toMergeID),
    )).toBe(true);
});

it('checks a facility list item to see whether any matches have been set to inactive', () => {
    const listItemWithAllMatchesActive = {
        matches: [
            {
                is_active: true,
            },
            {
                is_active: true,
            },
        ],
    };

    expect(anyListItemMatchesAreInactive(listItemWithAllMatchesActive)).toBe(false);

    const listItemWithInactiveMatches = {
        matches: [
            {
                is_active: false,
            },
            {
                is_active: false,
            },
        ],
    };

    expect(anyListItemMatchesAreInactive(listItemWithInactiveMatches)).toBe(true);
});

it('pluralizes a results count correclty, returning null if count is undefined or null', () => {
    expect(pluralizeResultsCount(undefined)).toBeNull();
    expect(pluralizeResultsCount(null)).toBeNull();
    expect(pluralizeResultsCount(1)).toBe('1 result');
    expect(pluralizeResultsCount(0)).toBe('0 results');
    expect(pluralizeResultsCount(200)).toBe('200 results');
});

it('removes duplicate entries from other locations data', () => {
    const entryWithNoDuplicates = [
        {
            lat: 1,
            lng: 1,
            contributor_id: 1,
            contributor_name: 'one',
        },
        {
            lat: 2,
            lng: 2,
            contributor_id: 2,
            contributor_name: 'two',
        },
    ];

    expect(removeDuplicatesFromOtherLocationsData(entryWithNoDuplicates)).toHaveLength(2);

    const entryWithDuplicate = [
        {
            lat: 1,
            lng: 1,
            contributor_id: 1,
            contributor_name: 'one',
        },
        {
            lat: 1,
            lng: 1,
            contributor_id: 1,
            contributor_name: 'one',
        },
    ];

    expect(removeDuplicatesFromOtherLocationsData(entryWithDuplicate)).toHaveLength(1);

    const entryWithDuplicateLocationButDifferentContributor = [
        {
            lat: 1,
            lng: 1,
            contributor_id: 1,
            contributor_name: 'one',
        },
        {
            lat: 1,
            lng: 1,
            contributor_id: 2,
            contributor_name: 'two',
        },
    ];

    expect(
        removeDuplicatesFromOtherLocationsData(entryWithDuplicateLocationButDifferentContributor),
    ).toHaveLength(2);

    const entryWithDuplicateLocationWithNoContributor = [
        {
            lat: 1,
            lng: 1,
            contributor_id: 1,
            contributor_name: 'one',
        },
        {
            lat: 1,
            lng: 1,
        },
    ];

    expect(
        removeDuplicatesFromOtherLocationsData(entryWithDuplicateLocationWithNoContributor),
    ).toHaveLength(1);

    const entryWithDuplicateContributorWithDifferentLocation = [
        {
            lat: 1,
            lng: 1,
            contributor_id: 1,
            contributor_name: 'one',
        },
        {
            lat: 1.1,
            lng: 1.1,
            contributor_id: 1,
            contributor_name: 'one',
        },
    ];

    expect(
        removeDuplicatesFromOtherLocationsData(entryWithDuplicateContributorWithDifferentLocation),
    ).toHaveLength(2);
});

it('should return an array with dashboard link if user has dashboard access', () => {
    const user = { is_superuser: true };
    const logoutAction = jest.fn();
    const activeFeatureFlags = [];

    const result = createUserDropdownLinks(user, logoutAction, activeFeatureFlags);

    expect(result).toContainEqual({
      label: 'Dashboard',
      href: dashboardRoute,
    });
});

it('should return an array without dashboard link if user does not have dashboard access', () => {
    const user = { is_superuser: false };
    const logoutAction = jest.fn();
    const activeFeatureFlags = [];

    const result = createUserDropdownLinks(user, logoutAction, activeFeatureFlags);

    expect(result).not.toContainEqual({
      label: 'Dashboard',
      href: dashboardRoute,
    });
});

it('should return an array with claimed facility link if active feature flag is present', () => {
    const user = { is_superuser: true };
    const logoutAction = jest.fn();
    const activeFeatureFlags = [CLAIM_A_FACILITY];

    const result = createUserDropdownLinks(user, logoutAction, activeFeatureFlags);

    expect(result).toContainEqual({
        label: 'My Facilities',
        href: '/claimed',
    });
});

it('extracts the ID from a valid URL without a trailing slash', () => {
    const url = '/contribute/single-location/search/id/BD202034606B9SA';
    expect(getLastPathParameter(url)).toBe('BD202034606B9SA');
});

it('extracts the ID from a valid URL with a trailing slash', () => {
    const url = '/contribute/single-location/search/id/BD202034606B9SA/';
    expect(getLastPathParameter(url)).toBe('BD202034606B9SA');
});

it('returns id when the URL ends at "id/" with no ID', () => {
    const url = '/contribute/single-location/search/id/';
    expect(getLastPathParameter(url)).toBe('id');
});

it('returns the correct ID when the URL contains query parameters', () => {
    const url = '/contribute/single-location/search/id/BD202034606B9SA?foo=bar';
    expect(getLastPathParameter(url)).toBe('BD202034606B9SA');
});

it('returns the correct ID when the URL has multiple segments after "id/"', () => {
    const url = '/contribute/single-location/search/id/BD202034606B9SA/extra';
    expect(getLastPathParameter(url)).toBe('extra');
});

it('returns the whole string if no slashes exist', () => {
    const url = 'BD202034606B9SA';
    expect(getLastPathParameter(url)).toBe('BD202034606B9SA');
});

it('returns empty string for an empty string', () => {
    const url = '';
    expect(getLastPathParameter(url)).toBe('');
});

it('returns empty string for a URL that only contains slashes', () => {
    const url = '///';
    expect(getLastPathParameter(url)).toBe('');
});

it('should return { min: value, max: value } when value is a number', () => {
    expect(generateRangeField(10)).toEqual({ min: 10, max: 10 });
    expect(generateRangeField(0)).toEqual({ min: 0, max: 0 });
    expect(generateRangeField(-5)).toEqual({ min: -5, max: -5 });
});

it('should return { min, max } when value is a valid range string', () => {
    expect(generateRangeField('10-20')).toEqual({ min: 10, max: 20 });
    expect(generateRangeField('0-100')).toEqual({ min: 0, max: 100 });
    expect(generateRangeField('-5-5')).toEqual({ min: 0, max: 5 });
});

it('should return { min: value, max: value } when value is a single string (not a range)', () => {
    expect(generateRangeField('15')).toEqual({ min: 15, max: 15 });
    expect(generateRangeField('test')).toEqual({ min: NaN, max: NaN });
});

it('should return { min: value, max: value } when value is an empty string', () => {
    expect(generateRangeField('')).toEqual({ min: 0, max: 0 });
});

it('should return { min, max } correctly when value has extra spaces', () => {
    expect(generateRangeField(' 10 - 20 ')).toEqual({ min: 10, max: 20 });
    expect(generateRangeField('  5 -   15')).toEqual({ min: 5, max: 15 });
});

it('should return { min: value, max: value } for non-string and non-number values', () => {
    expect(generateRangeField(null)).toEqual({ min: 0, max: 0 });
    expect(generateRangeField(undefined)).toEqual({ min: NaN, max: NaN });
    expect(generateRangeField({})).toEqual({ min: NaN, max: NaN });
    expect(generateRangeField([])).toEqual({ min: 0, max: 0 });
});

it('should return the base fields correctly', () => {
    const input = {
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: { value: 'US' },
    };

    const expectedOutput = {
        source: 'SLC',
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: 'US',
    };

    expect(parseContribData(input)).toEqual(expectedOutput);
});


it('should process array fields and keep non-empty values', () => {
    const input = {
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: { value: 'US' },
        sector: ['Waste Management'],
        parentCompany: 'ParentCompanySingle',
        productType: ['Shirts', 'Pants'],
    };

    const expectedOutput = {
        source: 'SLC',
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: 'US',
        sector: ['Waste Management'],
        parent_company: 'ParentCompanySingle',
        product_type: ['Shirts', 'Pants'],
    };

    expect(parseContribData(input)).toEqual(expectedOutput);
});

it('should handle an empty array by not including the field', () => {
    const input = {
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: { value: 'US' },
        sector: [],
    };

    const expectedOutput = {
        source: 'SLC',
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: 'US',
    };

    expect(parseContribData(input)).toEqual(expectedOutput);
});

it('should handle number_of_workers correctly', () => {
    const input = {
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: { value: 'US' },
        numberOfWorkers: '15',
    };

    const expectedOutput = {
        source: 'SLC',
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: 'US',
        number_of_workers: { min: 15, max: 15 },
    };

    expect(parseContribData(input)).toEqual(expectedOutput);
});

it('should remove empty fields while keeping valid ones', () => {
    const input = {
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: { value: 'US' },
        sector: [],
        parentCompany: null,
        productType: undefined,
        locationType: ['RCRAInfo subtitle C (Hazardous waste handlers)'],
    };

    const expectedOutput = {
        source: 'SLC',
        name: 'KELLY- MOORE PAINT CO INC',
        address: '710 AUZERAIS AVE, SAN JOSE, CA, 95126',
        country: 'US',
        location_type: ['RCRAInfo subtitle C (Hazardous waste handlers)'],
    };

    expect(parseContribData(input)).toEqual(expectedOutput);
});

it('should return only the source field if all other values are empty', () => {
    const input = {
        name: '',
        address: '',
        country: null,
        sector: [],
        parentCompany: '',
        productType: undefined,
        locationType: null,
        processingType: '',
        numberOfWorkers: null,
    };

    const expectedOutput = {
        source: 'SLC',
    };

    expect(parseContribData(input)).toEqual(expectedOutput);
});

it('should convert incoming object with camelCase keys into snake_case to conform request payload format', () => {
    const input = {
        name: 'AJAX AUTO DISMANTLERS INC',
        address: '2895 3RD, SAN FRANCISCO, CA, 94107-0000',
        country: {
            value: 'US',
            label: 'United States'
        },
        sector: [
            {
                value: 'Waste Management',
                label: 'Waste Management'
            },
            {
                value: 'Recycling',
                label: 'Recycling'
            }
        ],
        productType: [
            {
                label: 'Bottles',
                value: 'Bottles'
            },
            {
                label: 'Pockets',
                value: 'Pockets'
            },
            {
                label: 'Domestic goods',
                value: 'Domestic goods'
            }
        ],
        locationType: [
            {
                value: 'Warehousing / Distribution',
                label: 'Warehousing / Distribution'
            },
            {
                value: 'Final Product Assembly',
                label: 'Final Product Assembly'
            },
            {
                value: 'Office / HQ',
                label: 'Office / HQ'
            }
        ],
        processingType: [
            {
                value: 'Assembly',
                label: 'Assembly'
            },
            {
                value: 'Cut & Sew',
                label: 'Cut & Sew'
            },
            {
                value: 'Warehousing / Distribution',
                label: 'Warehousing / Distribution'
            }
        ],
        numberOfWorkers: "20-35",
        parentCompany: "Ajax Parent Ltd."
    };

    const expectedOutput = {
        name: 'AJAX AUTO DISMANTLERS INC',
        address: '2895 3RD, SAN FRANCISCO, CA, 94107-0000',
        sector: [
            'Waste Management',
            'Recycling'
        ],
        product_type: [
            'Bottles',
            'Pockets',
            'Domestic goods'
        ],
        location_type: [
            'Warehousing / Distribution',
            'Final Product Assembly',
            'Office / HQ'
        ],
        processing_type: [
            'Assembly',
            'Cut & Sew',
            'Warehousing / Distribution'
        ],
        parent_company: 'Ajax Parent Ltd.',
        number_of_workers: {
            "min": 20,
            "max": 35
        },
        country: 'US',
        source: 'SLC'
    };

    expect(parseContribData(input)).toEqual(expectedOutput);
});

describe('isRequiredFieldValid', () => {
    it('should return true if the field has a value', () => {
        expect(isRequiredFieldValid('test')).toBe(true);
        expect(isRequiredFieldValid('  test  ')).toBe(true);
        expect(isRequiredFieldValid('test test')).toBe(true);
    });

    it('should return false if the field has no value', () => {
        expect(isRequiredFieldValid('')).toBe(false);
        expect(isRequiredFieldValid('     ')).toBe(false);
        expect(isRequiredFieldValid(null)).toBe(false);
        expect(isRequiredFieldValid(undefined)).toBe(false);
    });
});

describe('getSelectStyles', () => {
    const provided = {
        borderColor: 'grey',
        boxShadow: 'none',
        color: 'blue',
      };

    const stateFocused = { isFocused: true };
    const stateNotFocused = { isFocused: false };

    it('returns an object with control and placeholder functions', () => {
        const styles = getSelectStyles();
        expect(typeof styles.control).toBe('function');
        expect(typeof styles.placeholder).toBe('function');
    });

    it('applies PURPLE border and inset box shadow when focused and no error', () => {
        const styles = getSelectStyles();
        const controlStyles = styles.control(provided, stateFocused);
        expect(controlStyles.borderColor).toBe(COLOURS.PURPLE);
        expect(controlStyles.boxShadow).toBe(`inset 0 0 0 1px ${COLOURS.PURPLE}`);
    });

    it('applies RED border when error state is true', () => {
        const styles = getSelectStyles(true);
        const controlStyles = styles.control(provided, stateFocused);
        expect(controlStyles.borderColor).toBe(COLOURS.RED);
    });

    it('applies correct placeholder style when error state is true', () => {
        const styles = getSelectStyles(true);
        const placeholderStyles = styles.placeholder(provided);
        expect(placeholderStyles.opacity).toBe(0.7);
        expect(placeholderStyles.color).toBe(COLOURS.RED);
    });

    it('uses the provided color for placeholder when error state is false', () => {
        const styles = getSelectStyles();
        const placeholderStyles = styles.placeholder(provided);
        expect(placeholderStyles.opacity).toBe(0.7);
        expect(placeholderStyles.color).toBe(provided.color);
    });

    it('sets hover borderColor to "black" when not focused and no error', () => {
        const styles = getSelectStyles();
        const controlStyles = styles.control(provided, stateNotFocused);
        expect(controlStyles['&:hover']).toEqual({ borderColor: 'black' });
    });

    it('sets hover borderColor to false when error state is true', () => {
        const styles = getSelectStyles(true);
        const controlStyles = styles.control(provided, stateNotFocused);
        expect(controlStyles['&:hover']).toEqual({ borderColor: false });
    });
});

describe('getNumberOfWorkersValidationError', () => {
    it('clear error messages for number of workers field', () => {
        const expectedValueOfZeroText =
        'The value of zero is not valid. Enter a positive whole number or a valid range (e.g., 1-5).';
        const expectedLessThenOrEqualText =
            'Invalid range. The minimum value must be less than or equal to the maximum value.';
        const expectedInvalidEntryText = 'Invalid entry. The value cannot start from zero.';
        const expectedInvalidFormatText =
            'Invalid format. Enter a whole number or a valid numeric range (e.g., 1-5).';

        expect(getNumberOfWorkersValidationError('0')).toBe(expectedValueOfZeroText);
        expect(getNumberOfWorkersValidationError('0-3')).toBe(expectedValueOfZeroText);
        expect(getNumberOfWorkersValidationError('1-0')).toBe(expectedValueOfZeroText);
        expect(getNumberOfWorkersValidationError('500-300')).toBe(expectedLessThenOrEqualText);
        expect(getNumberOfWorkersValidationError('010')).toBe(expectedInvalidEntryText);
        expect(getNumberOfWorkersValidationError('1-')).toBe(expectedInvalidFormatText);
        expect(getNumberOfWorkersValidationError('some text or &$*_')).toBe(expectedInvalidFormatText);
        expect(getNumberOfWorkersValidationError('3.9')).toBe(expectedInvalidFormatText);
    });

    it('valid numberOfWorkers has no errors, invalid shows error message', () => {
        const expectedValueOfZeroText =
        'The value of zero is not valid. Enter a positive whole number or a valid range (e.g., 1-5).';

        expect(!isValidNumberOfWorkers('100') && getNumberOfWorkersValidationError('100')).toBe(false);
        expect(!isValidNumberOfWorkers('0-300') && getNumberOfWorkersValidationError('0-300')).toBe(expectedValueOfZeroText);
    });
 })

describe('snakeToTitleCase', () => {
    it('converts snake_case to Title Case', () => {
        expect(snakeToTitleCase('hello_world')).toBe('Hello World');
        expect(snakeToTitleCase('my_variable_name')).toBe('My Variable Name');
    });

    it('returns an empty string when input is empty', () => {
        expect(snakeToTitleCase('')).toBe('');
    });

    it('handles single-word input', () => {
        expect(snakeToTitleCase('word')).toBe('Word');
    });

    it('handles input with multiple underscores', () => {
        expect(snakeToTitleCase('one__two___three')).toBe('One Two Three');
    });

    it('handles already capitalized input', () => {
        expect(snakeToTitleCase('Already_Title_Case')).toBe('Already Title Case');
    });
});

describe('slcValidationSchema', () => {
    const trimTextValidationError = 'Remove spaces at start and end of text.';
    const numberOfWorkersValidationError = 'Enter a single positive number ' +
        '(e.g., 5) or a valid range (e.g., 3–10). In a range, the minimum ' +
        'value must be less than or equal to the maximum, and both must ' +
        'be at least 1.';

    it('passes when all fields are valid', async () => {
        const data = {
            name: 'Factory X',
            address: '456 Main Ave',
            country: { value: 'PL', label: 'Poland' },
            numberOfWorkers: '10-100',
            productType: [{label: 'Shirts', value: 'Shirts'}],
            parentCompany: 'Global Parent',
        };
        await expect(slcValidationSchema.validate(data)).resolves.toEqual(data);
    });

    // Name field.
    it('fails when name is missing', async () => {
        const data = {
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow('Name is required.');
    });

    it('fails when name has trailing and leading spaces', async () => {
        const data = {
            name: ' Silverline Textiles Co. ',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(trimTextValidationError);
    });

    it('fails when name is a positive integer', async () => {
        const data = {
            name: '43546547',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Name cannot be a number.'
        );
    });

    it('fails when name is a negative integer', async () => {
        const data = {
            name: '-43546547',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Name cannot be a number.'
        );
    });

    it('fails when name is a float number', async () => {
        const data = {
            name: '-43546547.2',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Name cannot be a number.'
        );
    });
    
    it('fails when name is only spaces or symbols', async () => {
        const data = {
            name: "!!!&^#*#*(#(@# &@ %?/~ &#'",
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Name cannot contain only spaces or symbols.'
        );
    });

    it('fails when name exceeds 200 characters', async () => {
        const data = {
            name: 'The International Association for Sustainable Manufacturing and Textile Innovation Research Collaborative of North-East Asia and Global Development Solutions Unlimited Partners Incorporated The International Association',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Name cannot exceed 200 characters.'
        );
    });

    // Address field.
    it('fails when address is missing', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow('Address is required.');
    });

    it('fails when address has trailing and leading spaces', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: ' 742 Evergreen Terrace ',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            trimTextValidationError
        );
    });

    it('fails when address is a positive integer', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '43546547',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Address cannot be a number.'
        );
    });

    it('fails when address is a negative integer', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '-43546547',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Address cannot be a number.'
        );
    });

    it('fails when address is a float number', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '-43546547.2',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Address cannot be a number.'
        );
    });
    
    it('fails when address is only spaces or symbols', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: "!!!&^#*#*(#(@# &@ %?/~ &#'",
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Address cannot contain only spaces or symbols.'
        );
    });

    it('fails when address exceeds 200 characters', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '1283 Hollow Pine Industrial Estate, Block C, Floor 4, Unit 17B, Riverside Tech Park, Northbridge District, Westonborough, State of Orlanda, ZIP 84930-2298, United States of Arcania, United States of Arcania',
            country: { value: 'AI', label: 'Anguilla' }
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Address cannot exceed 200 characters.'
        );
    });

    // Country field.
    it('fails when country is missing', async () => {
        const data = { name: 'Valid', address: '123 Street' };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Country is required.'
        );
    });

    // Product type field.
    it('fails when more than 50 values are provided in the product type field', async () => {
        const data = {
            name: 'Valid Name',
            address: '123 Street',
            country: { value: 'AI', label: 'Anguilla' },
            productType: new Array(51).fill('Shoes'),
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Maximum of 50 product types allowed.'
        );
    });

    // Number of workers field.
    it('fails when number of workers has trailing and leading spaces', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            numberOfWorkers: '1 '
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Remove spaces at start and end of entry.'
        );
    });

    it('fails when number of workers is 0', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            numberOfWorkers: '0'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            numberOfWorkersValidationError
        );
    });
    
    it('fails when number of workers is a reverse range', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            numberOfWorkers: '100-5'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            numberOfWorkersValidationError
        );
    });
    
    it('fails when number of workers starts with 0', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            numberOfWorkers: '01-05'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            numberOfWorkersValidationError
        );
    });
    
    it('fails when number of workers format is invalid (range with dash only)', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            numberOfWorkers: '1-' };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            numberOfWorkersValidationError
        );
    });
    
    it('fails when number of workers format is invalid (non-numeric)', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            numberOfWorkers: 'abc'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            numberOfWorkersValidationError
        );
    });
    
    it('fails when number of workers has decimal', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'US' },
            numberOfWorkers: '3.5'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            numberOfWorkersValidationError
        );
    });

    // Parent company field.
    it('fails when parent company has trailing and leading spaces', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            parentCompany: ' Global Parent '
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            trimTextValidationError
        );
    });

    it('fails when parent company is a positive integer', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            parentCompany: '3435345'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Parent company cannot be a number.'
        );
    });

    it('fails when parent company is a negative integer', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            parentCompany: '-3435345'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Parent company cannot be a number.'
        );
    });

    it('fails when parent company is a float number', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            parentCompany: '-3435345.3232'
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Parent company cannot be a number.'
        );
    });
    
    it('fails when parent company is only spaces or symbols', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            parentCompany: "!!!&^#*#*(#(@# &@ %?/~ &#'",
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Parent company cannot contain only spaces or symbols.'
        );
    });

    it('fails when parent company exceeds 200 characters', async () => {
        const data = {
            name: 'Silverline Textiles Co.',
            address: '742 Evergreen Terrace',
            country: { value: 'AI', label: 'Anguilla' },
            parentCompany: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip.',
        };
        await expect(slcValidationSchema.validate(data)).rejects.toThrow(
            'Parent company cannot exceed 200 characters.'
        );
    });
});

describe('formatExtendedField', () => {
    const baseProps = {
        created_at: '2025-10-01T12:00:00Z',
        contributor_name: 'Test Contributor',
        is_verified: true,
        is_from_claim: false,
    };

    it('formats value with default formatter and fallback key', () => {
        const result = formatExtendedField({
            ...baseProps,
            value: ['Alpha', 'Beta'],
            field_name: 'native_language_name',
        });

        expect(result.secondary).toBe('October 1, 2025 by Test Contributor');
        expect(result.embeddedSecondary).toBe('October 1, 2025');
        expect(result.isVerified).toBe(true);
        expect(result.isFromClaim).toBe(false);
        expect(result.primary).toHaveLength(2);
        expect(result.primary[0].props.children).toBe('Alpha');
        expect(result.primary[1].props.children).toBe('Beta');
    });

    it('formats parent_company_os_id values as links', () => {
        const value = ['US202511345DVTE', 'US202511345DFSD'];
        const result = formatExtendedField({
            ...baseProps,
            value,
            field_name: 'parent_company_os_id',
        });

        expect(result.primary).toHaveLength(2);
        result.primary.forEach((element, idx) => {
            expect(element.type).toBe('a');
            expect(element.props.href).toBe(`/facilities/${value[idx]}`);
            expect(element.props.children).toBe(value[idx]);
        });
    });

    it('uses custom formatValue function', () => {
        const result = formatExtendedField({
            ...baseProps,
            value: ['ABC'],
            field_name: 'test_field',
            formatValue:  rawValue => rawValue.map(string => string.toLowerCase()),
        });

        expect(result.primary).toHaveLength(1);
        expect(result.primary[0].props.children).toBe('abc');
    });

    it('handles empty value array', () => {
        const result = formatExtendedField({
            ...baseProps,
            value: [],
            field_name: 'test_field',
        });

        expect(result.primary).toHaveLength(0);
    });

    it('handles non-array value', () => {
        const result = formatExtendedField({
            ...baseProps,
            value: 'SingleValue',
            field_name: 'test_field',
        });

        expect(result.primary).toBe('SingleValue');
        expect(result.secondary).toBe('October 1, 2025 by Test Contributor');
        expect(result.embeddedSecondary).toBe('October 1, 2025');
        expect(result.isVerified).toBe(true);
        expect(result.isFromClaim).toBe(false);
    });
});

describe('processDromoResults', () => {
    let originalBlob;
    let originalFile;
    let originalDataTransfer;
    let fileInput;
    let updateFileName;

    beforeAll(() => {
        // Mock Blob, File, DataTransfer for the test environment
        originalBlob = global.Blob;
        originalFile = global.File;
        originalDataTransfer = global.DataTransfer;

        global.Blob = function (content, options) {
            this.content = content;
            this.options = options;
        };
        global.File = function (content, name, options) {
            this.content = content;
            this.name = name;
            this.options = options;
        };
        global.DataTransfer = function () {
            this.items = {
                files: [],
                add(file) {
                    this.files.push(file);
                },
            };
            Object.defineProperty(this, 'files', {
                get: () => this.items.files,
            });
        };
    });

    afterAll(() => {
        global.Blob = originalBlob;
        global.File = originalFile;
        global.DataTransfer = originalDataTransfer;
    });

    beforeEach(() => {
        fileInput = { current: { files: null } };
        updateFileName = jest.fn();
        jest.spyOn(console, 'log').mockImplementation(() => {});
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    it('should do nothing if results is undefined', () => {
        processDromoResults(undefined, 'file.xlsx', fileInput, updateFileName);
        expect(updateFileName).not.toHaveBeenCalled();
        expect(fileInput.current.files).toBeNull();
    });

    it('should do nothing if results is empty', () => {
        processDromoResults([], 'file.xlsx', fileInput, updateFileName);
        expect(updateFileName).not.toHaveBeenCalled();
        expect(fileInput.current.files).toBeNull();
    });

    it('should process results and update file input', () => {
        const results = [
            { name: 'Alice', age: 30 },
            { name: 'Bob', age: 25 },
        ];
        processDromoResults(results, 'file.xlsx', fileInput, updateFileName);

        expect(fileInput.current.files).toHaveLength(1);
        const file = fileInput.current.files[0];
        expect(file.name).toBe('file.csv');
        expect(file.options.type).toBe('text/csv');

        expect(updateFileName).toHaveBeenCalledWith(fileInput);
    });

    it('should not update file input if fileInput.current is null', () => {
        const results = [{ name: 'Alice', age: 30 }];
        fileInput.current = null;
        processDromoResults(results, 'file.xlsx', fileInput, updateFileName);
        expect(updateFileName).not.toHaveBeenCalled();
    });
});

describe('formatPartnerFieldValue', () => {
    const emptyItem = {};

    it('formats raw_value as a single value', () => {
        const value = { raw_value: 'Test Value' };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('Test Value');
    });

    it('formats raw_value with number', () => {
        const value = { raw_value: 100 };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe(100);
    });

    it('formats raw_values as array joined by comma', () => {
        const value = { raw_values: ['Value 1', 'Value 2', 'Value 3'] };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('Value 1, Value 2, Value 3');
    });

    it('formats empty array as empty string', () => {
        const value = { raw_values: [] };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('');
    });

    it('formats single-item array as string without comma', () => {
        const value = { raw_values: ['Single Value'] };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('Single Value');
    });

    it('formats raw_values as object with key-value pairs', () => {
        const value = { raw_values: { test_1: '1', test_2: '2' } };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('test_1: 1, test_2: 2');
    });

    it('formats empty object as empty string', () => {
        const value = { raw_values: {} };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('');
    });

    it('formats raw_values object with nested values', () => {
        const value = { raw_values: { key1: 'value1', key2: 100, key3: 'value3' } };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('key1: value1, key2: 100, key3: value3');
    });

    it('formats pipe-delimited string into array (legacy format)', () => {
        const value = { raw_values: 'value1|value2|value3' };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toEqual(['value1', 'value2', 'value3']);
    });

    it('formats single string value without pipe', () => {
        const value = { raw_values: 'single value' };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toEqual(['single value']);
    });

    it('returns plain value if no raw_value or raw_values property', () => {
        const value = 'Plain String Value';
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('Plain String Value');
    });

    it('returns numeric value if no raw_value or raw_values property', () => {
        const value = 42;
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe(42);
    });

    it('prefers raw_values over raw_value when both exist', () => {
        const value = { raw_value: 'ignored', raw_values: ['preferred'] };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('preferred');
    });

    it('falls back to raw_value when raw_values is undefined', () => {
        const value = { raw_value: 'fallback value' };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('fallback value');
    });

    it('formats array with mixed types', () => {
        const value = { raw_values: ['string', 123, 'another'] };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('string, 123, another');
    });

    it('formats object with boolean and null values', () => {
        const value = { raw_values: { active: true, deleted: false, notes: null } };
        const result = formatPartnerFieldValue(value, emptyItem);
        expect(result).toBe('active: true, deleted: false, notes: null');
    });

    describe('with JSON schema formatting', () => {
        it('formats URI field with _text property as clickable link', () => {
            const value = {
                raw_value: {
                    url: 'https://example.com/audit-123',
                    url_text: 'View Audit Report',
                },
            };
            const item = {
                json_schema: {
                    type: 'object',
                    properties: {
                        url: {
                            type: 'string',
                            format: 'uri',
                        },
                        url_text: {
                            type: 'string',
                        },
                    },
                },
            };
            const result = formatPartnerFieldValue(value, item);

            expect(Array.isArray(result)).toBe(true);
            expect(result.length).toBe(1);
            expect(result[0].type).toBe('div');
            expect(result[0].props.children.type).toBe('a');
            expect(result[0].props.children.props.href).toBe(
                'https://example.com/audit-123',
            );
            expect(result[0].props.children.props.children).toBe(
                'View Audit Report',
            );
            expect(result[0].props.children.props.target).toBe('_blank');
            expect(result[0].props.children.props.rel).toBe(
                'noopener noreferrer',
            );
        });

        it('formats URI field without _text property, using URI as link text', () => {
            const value = {
                raw_value: {
                    mit_data_url: 'https://livingwage.mit.edu/locations/123',
                },
            };
            const item = {
                json_schema: {
                    type: 'object',
                    properties: {
                        mit_data_url: {
                            type: 'string',
                            format: 'uri',
                        },
                    },
                },
            };
            const result = formatPartnerFieldValue(value, item);

            expect(Array.isArray(result)).toBe(true);
            expect(result.length).toBe(1);
            expect(result[0].type).toBe('div');
            expect(result[0].props.children.type).toBe('a');
            expect(result[0].props.children.props.href).toBe(
                'https://livingwage.mit.edu/locations/123',
            );
            expect(result[0].props.children.props.children).toBe(
                'https://livingwage.mit.edu/locations/123',
            );
        });

        it('formats non-URI field with title as "Title: value"', () => {
            const value = {
                raw_value: {
                    internal_id: 'abc-123-xyz',
                },
            };
            const item = {
                json_schema: {
                    type: 'object',
                    properties: {
                        internal_id: {
                            type: 'string',
                            title: 'Internal ID',
                        },
                    },
                },
            };
            const result = formatPartnerFieldValue(value, item);

            expect(Array.isArray(result)).toBe(true);
            expect(result.length).toBe(1);
            expect(result[0].type).toBe('div');
            expect(result[0].props.children).toBe('Internal ID: abc-123-xyz');
        });

        it('formats non-URI field without title as plain value', () => {
            const value = {
                raw_value: {
                    notes: 'Some notes here',
                },
            };
            const item = {
                json_schema: {
                    type: 'object',
                    properties: {
                        notes: {
                            type: 'string',
                        },
                    },
                },
            };
            const result = formatPartnerFieldValue(value, item);

            expect(Array.isArray(result)).toBe(true);
            expect(result.length).toBe(1);
            expect(result[0].type).toBe('div');
            expect(result[0].props.children).toBe('Some notes here');
        });

        it('formats mixed URI and non-URI fields with titles', () => {
            const value = {
                raw_value: {
                    url: 'https://example.com/report',
                    url_text: 'View Report',
                    internal_id: 'ABC-123',
                    status: 'active',
                },
            };
            const item = {
                json_schema: {
                    type: 'object',
                    properties: {
                        url: {
                            type: 'string',
                            format: 'uri',
                        },
                        url_text: {
                            type: 'string',
                        },
                        internal_id: {
                            type: 'string',
                            title: 'Internal ID',
                        },
                        status: {
                            type: 'string',
                            title: 'Status',
                        },
                    },
                },
            };
            const result = formatPartnerFieldValue(value, item);

            expect(Array.isArray(result)).toBe(true);
            expect(result.length).toBe(3); // url, internal_id, status (url_text is skipped)

            const urlElement = result.find(
                r =>
                    r.props.children?.type === 'a' &&
                    r.props.children?.props?.href ===
                        'https://example.com/report',
            );
            expect(urlElement).toBeDefined();
            expect(urlElement.props.children.props.children).toBe(
                'View Report',
            );

            const internalIdElement = result.find(
                r =>
                    typeof r.props.children === 'string' &&
                    r.props.children.includes('Internal ID: ABC-123'),
            );
            expect(internalIdElement).toBeDefined();

            const statusElement = result.find(
                r =>
                    typeof r.props.children === 'string' &&
                    r.props.children.includes('Status: active'),
            );
            expect(statusElement).toBeDefined();
        });

        it('formats object without URI fields using plain formatting with titles', () => {
            const value = {
                raw_value: {
                    name: 'John Doe',
                    age: 30,
                    email: 'john@example.com',
                },
            };
            const item = {
                json_schema: {
                    type: 'object',
                    properties: {
                        name: {
                            type: 'string',
                            title: 'Full Name',
                        },
                        age: {
                            type: 'integer',
                            title: 'Age',
                        },
                        email: {
                            type: 'string',
                            title: 'Email Address',
                        },
                    },
                },
            };
            const result = formatPartnerFieldValue(value, item);

            expect(Array.isArray(result)).toBe(true);
            expect(result.length).toBe(3);

            expect(result[0].props.children).toBe('Full Name: John Doe');
            expect(result[1].props.children).toBe('Age: 30');
            expect(result[2].props.children).toBe('Email Address: john@example.com');
        });
    });
});
