import React from 'react';
import ArrowUpwardIcon from '@material-ui/icons/ArrowUpward';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';
import COLOURS from './COLOURS';

export const DEFAULT_SORT_OPTION_INDEX = 2;
export const OTHER = 'Other';
export const FACILITIES_REQUEST_PAGE_SIZE = 50;
export const FACILITIES_DOWNLOAD_LIMIT = 10000;
export const FREE_FACILITIES_DOWNLOAD_LIMIT = 5000;
export const FACILITIES_DOWNLOAD_REQUEST_PAGE_SIZE = 100;

export const WEB_HEADER_HEIGHT = '160px';
export const MOBILE_HEADER_HEIGHT = '140px';

export const CONFIRM_ACTION = 'confirm';
export const MERGE_ACTION = 'merge';
export const REJECT_ACTION = 'reject';

export const InfoLink = 'https://info.opensupplyhub.org';

export const EMPTY_PLACEHOLDER = 'N/A';

export const InfoPaths = {
    storiesResources: 'stories-resources',
    privacyPolicy: 'privacy-policy',
    dataCleaningService: 'data-cleaning-service',
    preparingData: 'resources/preparing-data',
    dataQuality: 'resources/a-free-universal-id-matching-algorithm',
    claimedFacilities: 'stories-resources/claim-a-facility',
    termsOfService: 'terms-of-service',

    // How It Works
    home: '',
    faqs: 'faqs',
    brands: 'brands',
    civilSociety: 'civil-society',
    facilities: 'facilities',
    multiStakeholderInitiatives: 'msis',
    researchers: 'researchers',
    serviceProviders: 'service-providers',
    sectors: 'sectors',
    technology: 'technology',
    developerResources: 'developer-resources',
    api: 'api',
    embeddedMap: 'embedded-map',
    donate: 'donate',

    // About Us
    mission: 'mission',
    supporters: 'supporters',
    press: 'press',
    financials: 'financials',
    governanceAndPolicies: 'governance-policies',
    team: 'team',
    boardOfDirectors: 'board',
    workWithUs: 'work-with-us',
    contactUs: 'contact-us',

    // Other
    resources: 'resources',
    pricing: 'pricing',

    // Footer
    mediaHub: 'media-hub',
};

export const InfoResourcesQuery = {
    // Resources
    caseStudy: 'case-study',
    guide: 'guide',
    video: 'video',
};

// This choices must be kept in sync with the identical list
// kept in the Django API's models.py file
export const contributorTypeOptions = Object.freeze([
    'Academic / Researcher / Journalist / Student',
    'Auditor / Certification Scheme / Service Provider',
    'Brand / Retailer',
    'Civil Society Organization',
    'Facility / Factory / Manufacturing Group / Supplier / Vendor',
    'Multi-Stakeholder Initiative',
    'Union',
    OTHER,
]);

export const facilityClaimStatusChoicesEnum = Object.freeze({
    PENDING: 'PENDING',
    APPROVED: 'APPROVED',
    DENIED: 'DENIED',
    REVOKED: 'REVOKED',
});
export const facilityClaimStatusChoices = [
    { value: facilityClaimStatusChoicesEnum.PENDING, label: 'PENDING' },
    { value: facilityClaimStatusChoicesEnum.APPROVED, label: 'APPROVED' },
    { value: facilityClaimStatusChoicesEnum.DENIED, label: 'DENIED' },
    { value: facilityClaimStatusChoicesEnum.REVOKED, label: 'REVOKED' },
];

export const facilityListStatusChoicesEnum = Object.freeze({
    PENDING: 'PENDING',
    APPROVED: 'APPROVED',
    REJECTED: 'REJECTED',
    MATCHED: 'MATCHED',
    REPLACED: 'REPLACED',
});
export const facilityListStatusChoices = [
    { value: facilityListStatusChoicesEnum.MATCHED, label: 'Matched' },
    { value: facilityListStatusChoicesEnum.PENDING, label: 'Pending' },
    { value: facilityListStatusChoicesEnum.APPROVED, label: 'Approved' },
    { value: facilityListStatusChoicesEnum.REJECTED, label: 'Rejected' },
    { value: facilityListStatusChoicesEnum.REPLACED, label: 'Replaced' },
];

// These choices must be kept in sync with the identical list
// kept in the Django API's constants.py file
export const matchResponsibilityEnum = Object.freeze({
    MODERATOR: 'moderator',
    CONTRIBUTOR: 'contributor',
});
export const matchResponsibilityChoices = [
    { value: 'moderator', label: 'OS Hub Admins' },
    { value: 'contributor', label: 'The contributor' },
];

export const inputTypesEnum = Object.freeze({
    text: 'text',
    password: 'password',
    select: 'select',
    checkbox: 'checkbox',
});

export const registrationFieldsEnum = Object.freeze({
    email: 'email',
    name: 'name',
    description: 'description',
    website: 'website',
    contributorType: 'contributorType',
    otherContributorType: 'otherContributorType',
    password: 'password',
    confirmPassword: 'confirmPassword',
    tos: 'tos',
    newsletter: 'newsletter',
});

export const profileFieldsEnum = Object.freeze({
    [registrationFieldsEnum.email]: registrationFieldsEnum.email,
    [registrationFieldsEnum.name]: registrationFieldsEnum.name,
    [registrationFieldsEnum.description]: registrationFieldsEnum.description,
    [registrationFieldsEnum.wesbite]: registrationFieldsEnum.website,
    [registrationFieldsEnum.contributorType]:
        registrationFieldsEnum.contributorType,
    [registrationFieldsEnum.otherContributorType]:
        registrationFieldsEnum.otherContributorType,
    currentPassword: 'currentPassword',
    newPassword: 'newPassword',
    confirmNewPassword: 'confirmNewPassword',
    isModerationMode: 'isModerationMode',
});

export const profileSummaryFieldsEnum = Object.freeze({
    facilityLists: 'facilityLists',
});

const accountEmailField = Object.freeze({
    id: registrationFieldsEnum.email,
    label: 'Email Address',
    type: inputTypesEnum.text,
    required: true,
    hint: null,
    modelFieldName: 'email',
    hideOnViewOnlyProfile: true,
});

const accountAdminSettingsField = Object.freeze({
    id: profileFieldsEnum.isModerationMode,
    label: 'Admin Settings',
    type: inputTypesEnum.checkbox,
    required: false,
    hint: null,
    modelFieldName: 'is_moderation_mode',
    hideOnViewOnlyProfile: true,
});

const accountNameField = Object.freeze({
    id: registrationFieldsEnum.name,
    label: 'Organization Name',
    type: inputTypesEnum.text,
    required: true,
    hint: `If you are uploading a supplier list on behalf of the organization
you work for, you should add the organization name here, not your personal name.
Your organization name will appear publicly on all facilities that you upload as
the data source for each facility contributed.`,
    modelFieldName: 'name',
});

const accountDescriptionField = Object.freeze({
    id: registrationFieldsEnum.description,
    label: 'Organization Description',
    type: inputTypesEnum.text,
    required: true,
    hint: `Enter a description of the organization. This will appear in your
public organization profile.`,
    modelFieldName: 'description',
});

const accountWebsiteField = Object.freeze({
    id: registrationFieldsEnum.website,
    label: 'Website',
    type: inputTypesEnum.text,
    required: false,
    hint: null,
    modelFieldName: 'website',
});

const accountContributorTypeField = Object.freeze({
    id: registrationFieldsEnum.contributorType,
    label: 'Organization Type',
    type: inputTypesEnum.select,
    options: contributorTypeOptions,
    required: true,
    modelFieldName: 'contributor_type',
});

const accountOtherContributorTypeField = Object.freeze({
    id: registrationFieldsEnum.otherContributorType,
    label: 'Other Contributor Type',
    type: inputTypesEnum.text,
    required: true,
    hint: 'Please specify',
    modelFieldName: 'other_contributor_type',
});

const accountPasswordField = Object.freeze({
    id: registrationFieldsEnum.password,
    label: 'Password',
    type: inputTypesEnum.password,
    required: true,
    modelFieldName: 'password',
    hideOnViewOnlyProfile: true,
});

const accountConfirmPasswordField = Object.freeze({
    id: registrationFieldsEnum.confirmPassword,
    label: 'Confirm Password',
    type: inputTypesEnum.password,
    required: true,
    modelFieldName: 'confirmPassword',
});

const accountCurrentPasswordField = Object.freeze({
    id: profileFieldsEnum.currentPassword,
    label: 'Current Password',
    header:
        'If you do not need to change your password leave these three password fields empty.',
    type: inputTypesEnum.password,
    modelFieldName: 'current_password',
    hideOnViewOnlyProfile: true,
    required: false,
});

const accountNewPasswordField = Object.freeze({
    id: profileFieldsEnum.newPassword,
    label: 'New Password',
    type: inputTypesEnum.password,
    modelFieldName: 'new_password',
    hideOnViewOnlyProfile: true,
    required: false,
});

const accountConfirmNewPasswordField = Object.freeze({
    id: profileFieldsEnum.confirmNewPassword,
    label: 'Confirm New Password',
    type: inputTypesEnum.password,
    modelFieldName: 'confirm_new_password',
    hideOnViewOnlyProfile: true,
    required: false,
});

const accountNewsletterField = Object.freeze({
    id: registrationFieldsEnum.newsletter,
    label:
        "I'd like to receive important email updates about OS Hub features and data.",
    modelFieldName: 'should_receive_newsletter',
    type: inputTypesEnum.checkbox,
});

const accountTOSField = Object.freeze({
    id: registrationFieldsEnum.tos,
    label: 'Terms of Service',
    link: Object.freeze({
        prefixText: 'Agree to ',
        url: `${InfoLink}/${InfoPaths.termsOfService}`,
    }),
    required: true,
    modelFieldName: 'has_agreed_to_terms_of_service',
    type: inputTypesEnum.checkbox,
});

export const registrationFormFields = Object.freeze([
    accountEmailField,
    accountNameField,
    accountDescriptionField,
    accountWebsiteField,
    accountContributorTypeField,
    accountOtherContributorTypeField,
    accountPasswordField,
    accountConfirmPasswordField,
    accountNewsletterField,
    accountTOSField,
]);

export const profileFormFields = Object.freeze([
    accountEmailField,
    accountAdminSettingsField,
    accountNameField,
    accountDescriptionField,
    accountWebsiteField,
    accountContributorTypeField,
    accountOtherContributorTypeField,
    accountCurrentPasswordField,
    accountNewPasswordField,
    accountConfirmNewPasswordField,
]);

export const mainRoute = '/';
export const settingsRoute = '/settings';
export const authLoginFormRoute = '/auth/login';
export const authRegisterFormRoute = '/auth/register';
export const authResetPasswordFormRoute = '/auth/resetpassword/:uid';
export const authConfirmRegistrationRoute = '/auth/confirm/:uid';
export const contributeRoute = '/contribute';
export const multipleLocationRoute = '/contribute/multiple-locations';
export const listsRoute = '/lists';
export const facilityListItemsRoute = '/lists/:listID';
export const facilitiesRoute = '/facilities';
export const facilityDetailsRoute = '/facilities/:osID';
export const claimFacilityRoute = '/facilities/:osID/claim';
export const profileRoute = '/profile/:id';
export const aboutProcessingRoute = `${InfoLink}/${InfoPaths.dataQuality}`;
export const dashboardRoute = '/dashboard';
export const dashboardListsRoute = '/dashboard/lists';
export const dashboardApiBlocksRoute = '/dashboard/apiblocks';
export const dashboardApiBlockRoute = '/dashboard/apiblocks/:blockId';
export const dashboardClaimsRoute = '/dashboard/claims';
export const dashboardModerationQueueRoute = '/dashboard/moderation-queue';
export const dashboardContributionRecordRoute =
    '/dashboard/moderation-queue/:moderationID';
export const dashboardDeleteFacilityRoute = '/dashboard/deletefacility';
export const dashboardMergeFacilitiesRoute = '/dashboard/mergefacilities';
export const dashboardAdjustFacilityMatchesRoute =
    '/dashboard/adjustfacilitymatches';
export const dashboardUpdateFacilityLocationRoute =
    '/dashboard/updatefacilitylocation';
export const dashboardActivityReportsRoute = '/dashboard/activityreports';
export const dashboardLinkOsIdRoute = '/dashboard/linkid';
export const dashboardGeocoderRoute = '/dashboard/geocoder';
export const claimedFacilitiesRoute = '/claimed';
export const claimedFacilitiesDetailRoute = '/claimed/:claimID';
export const dashboardClaimsDetailsRoute = '/dashboard/claims/:claimID';
export const aboutClaimedFacilitiesRoute = `${InfoLink}/${InfoPaths.claimedFacilities}`;
export const contributeProductionLocationRoute = '/contribute/single-location';
export const searchByOsIdResultRoute =
    '/contribute/single-location/search/id/:osID';
export const searchByNameAndAddressResultRoute =
    '/contribute/single-location/search/';
export const productionLocationInfoRouteCommon =
    '/contribute/single-location/info/';
export const productionLocationInfoRouteCreate =
    '/contribute/single-location/info/:moderationID?';
export const productionLocationInfoRouteUpdate =
    '/contribute/single-location/:osID/info/:moderationID?';

export const contributeFieldsEnum = Object.freeze({
    name: 'name',
    description: 'description',
});

export const contributeFileName = Object.freeze({
    id: contributeFieldsEnum.name,
    label: 'Enter the name for this facility list',
    hint: (
        <>
            example: <b>Your Organization’s Name</b> Facility List June 2023
        </>
    ),
    type: inputTypesEnum.text,
    placeholder: 'Facility List Name',
    required: true,
});

export const contributeFileDescription = Object.freeze({
    id: contributeFieldsEnum.description,
    label: `Enter a description of this facility list and include a timeframe
for the list's validity`,
    hint: (
        <>
            example: This is the <b>Your Organization’s Name</b> list of
            suppliers for their retail products valid from Jan 2023 to June 2023
        </>
    ),
    type: inputTypesEnum.text,
    placeholder: 'Facility List Description',
    required: false,
});

export const contributeFormFields = Object.freeze([
    contributeFileName,
    contributeFileDescription,
]);

export const contributeReplacesNoneSelectionID = -1;

// These values must be kept in sync with the tuple of STATUS_CHOICES
// declared on the API's FacilityListItem model. See:
// https://github.com/open-apparel-registry/open-apparel-registry/blob/a6e68960d3e1c547c7c2c1935fd28fde6108e3c6/src/django/api/models.py#L224

export const facilityListItemStatusChoicesEnum = Object.freeze({
    UPLOADED: 'UPLOADED',
    PARSED: 'PARSED',
    GEOCODED: 'GEOCODED',
    GEOCODED_NO_RESULTS: 'GEOCODED_NO_RESULTS',
    MATCHED: 'MATCHED',
    POTENTIAL_MATCH: 'POTENTIAL_MATCH',
    CONFIRMED_MATCH: 'CONFIRMED_MATCH',
    NEW_FACILITY: 'NEW_FACILITY', // This is not a status that appears in the database
    ERROR: 'ERROR',
    ERROR_PARSING: 'ERROR_PARSING',
    ERROR_GEOCODING: 'ERROR_GEOCODING',
    ERROR_MATCHING: 'ERROR_MATCHING',
    DELETED: 'DELETED',
    REMOVED: 'REMOVED', // This is not a status that appears in the database
    DUPLICATE: 'DUPLICATE',
    ITEM_REMOVED: 'ITEM_REMOVED',
});

export const facilityListItemErrorStatuses = Object.freeze([
    facilityListItemStatusChoicesEnum.ERROR,
    facilityListItemStatusChoicesEnum.ERROR_PARSING,
    facilityListItemStatusChoicesEnum.ERROR_GEOCODING,
    facilityListItemStatusChoicesEnum.ERROR_MATCHING,
]);

export const facilityListStatusFilterChoices = Object.freeze([
    {
        label: facilityListItemStatusChoicesEnum.UPLOADED,
        value: facilityListItemStatusChoicesEnum.UPLOADED,
    },
    {
        label: facilityListItemStatusChoicesEnum.PARSED,
        value: facilityListItemStatusChoicesEnum.PARSED,
    },
    {
        label: facilityListItemStatusChoicesEnum.GEOCODED,
        value: facilityListItemStatusChoicesEnum.GEOCODED,
    },
    {
        label: facilityListItemStatusChoicesEnum.GEOCODED_NO_RESULTS,
        value: facilityListItemStatusChoicesEnum.GEOCODED_NO_RESULTS,
    },
    {
        label: facilityListItemStatusChoicesEnum.MATCHED,
        value: facilityListItemStatusChoicesEnum.MATCHED,
    },
    {
        label: facilityListItemStatusChoicesEnum.POTENTIAL_MATCH,
        value: facilityListItemStatusChoicesEnum.POTENTIAL_MATCH,
    },
    {
        label: facilityListItemStatusChoicesEnum.CONFIRMED_MATCH,
        value: facilityListItemStatusChoicesEnum.CONFIRMED_MATCH,
    },
    {
        label: facilityListItemStatusChoicesEnum.NEW_FACILITY,
        value: facilityListItemStatusChoicesEnum.NEW_FACILITY,
    },
    {
        label: facilityListItemStatusChoicesEnum.DUPLICATE,
        value: facilityListItemStatusChoicesEnum.DUPLICATE,
    },
    {
        label: facilityListItemStatusChoicesEnum.ERROR,
        value: facilityListItemStatusChoicesEnum.ERROR,
    },
    {
        label: facilityListItemStatusChoicesEnum.ERROR_PARSING,
        value: facilityListItemStatusChoicesEnum.ERROR_PARSING,
    },
    {
        label: facilityListItemStatusChoicesEnum.ERROR_GEOCODING,
        value: facilityListItemStatusChoicesEnum.ERROR_GEOCODING,
    },
    {
        label: facilityListItemStatusChoicesEnum.ERROR_MATCHING,
        value: facilityListItemStatusChoicesEnum.ERROR_MATCHING,
    },
    {
        label: facilityListItemStatusChoicesEnum.DELETED,
        value: facilityListItemStatusChoicesEnum.DELETED,
    },
    {
        label: facilityListItemStatusChoicesEnum.REMOVED,
        value: facilityListItemStatusChoicesEnum.REMOVED,
    },
]);

export const facilityListSummaryStatusMessages = Object.freeze({
    ERROR: 'Some items failed to be processed.',
    AWAITING: 'Some potential matches require your feedback.',
    PROCESSING: 'The list is still being processed.',
    COMPLETED: 'This list has been processed successfully.',
    REJECTED: 'This list was rejected and will not be processed.',
});

export const listUploadTroubleshootingEmail = 'support@opensupplyhub.org';

export const DEFAULT_PAGE = 1;
export const DEFAULT_ROWS_PER_PAGE = 20;
export const rowsPerPageOptions = Object.freeze([
    DEFAULT_ROWS_PER_PAGE,
    50,
    100,
]);

export const FEATURE = 'Feature';
export const POINT = 'Point';
export const FEATURE_COLLECTION = 'FeatureCollection';

// These values must be kept in sync with the tuple of STATUS_CHOICES
// declared on the API's FacilityMatch model.
export const facilityMatchStatusChoicesEnum = Object.freeze({
    PENDING: 'PENDING',
    AUTOMATIC: 'AUTOMATIC',
    CONFIRMED: 'CONFIRMED',
    REJECTED: 'REJECTED',
    MERGED: 'MERGED',
});

export const emptyFeatureCollection = Object.freeze({
    type: FEATURE_COLLECTION,
    features: Object.freeze([]),
});

export const ENTER_KEY = 'Enter';

export const facilitiesListTableTooltipTitles = Object.freeze({
    uploaded: 'Total number of items that have been uploaded.',
    duplicates:
        'Number of items identified as a duplicate of another item in the same list.',
    errors: 'Number of errors that occurred during processing.',
    status: 'Processing status of this list.',
});

export const userApiInfoTooltipTitles = Object.freeze({
    apiCallAllowance:
        'Call Limit is the number of calls your account can make per renewal period.',
    currentCallCount:
        'Current Usage is the number of calls your account has made within the current renewal period.',
    renewalPeriod:
        'Renewal Period indicates how often your package renews. This can either be monthly or annually.',
});

export const IS_NOT_SET = 'Is not set';
export const CLAIM_A_FACILITY = 'claim_a_facility';
export const VECTOR_TILE = 'vector_tile';
export const REPORT_A_FACILITY = 'report_a_facility';
export const EMBEDDED_MAP_FLAG = 'embedded_map';
export const EXTENDED_PROFILE_FLAG = 'extended_profile';
export const DEFAULT_SEARCH_TEXT = 'Facility Name or OS ID';
export const DISABLE_LIST_UPLOADING = 'disable_list_uploading';
export const SHOW_ADDITIONAL_IDENTIFIERS = 'show_additional_identifiers';
export const PRIVATE_INSTANCE = 'private_instance';
export const ENABLE_DROMO_UPLOADING = 'enable_dromo_uploading';
export const ENABLE_V1_CLAIMS_FLOW = 'enable_v1_claims_flow';

export const DEFAULT_COUNTRY_CODE = 'IE';

export const claimAFacilityFormFields = Object.freeze({
    contactName: Object.freeze({
        id: 'contact-full-name',
        label: 'Contact person full name',
    }),
    contactEmail: Object.freeze({
        id: 'contact-email-address',
        label: 'Email',
    }),
    contactPhone: Object.freeze({
        id: 'contact-phone-number',
        label: 'Phone number',
    }),
    contactJobTitle: Object.freeze({
        id: 'contact-job-title',
        label: 'Job title',
    }),
    companyName: Object.freeze({
        id: 'company-name',
        label: 'Official name of LLC or company registered',
    }),
    parentCompany: Object.freeze({
        id: 'parent-company',
        label: 'Parent company / supplier group',
        aside: `If you cannot find the parent company / supplier group
        in this list consider inviting them to register with Open Supply Hub.`,
    }),
    website: Object.freeze({
        id: 'website',
        label: 'Facility website',
    }),
    facilityDescription: Object.freeze({
        id: 'facility-description',
        label: 'Facility bio/description',
    }),
    verificationMethod: Object.freeze({
        id: 'verification-method',
        label: 'Any additional details?',
    }),
    linkedinProfile: Object.freeze({
        id: 'linkedin-profile',
        label: 'Link to Facility LinkedIn Profile',
    }),
    claimAdditionalDocumentation: Object.freeze({
        id: 'claimant-additional-documentation',
        label:
            'Additional Documentation (e.g.: business card, employment verification letter on company letterhead, business registration documents)',
    }),
});

export const claimAFacilitySupportDocsFormFields = Object.freeze({
    contactYourName: Object.freeze({
        id: 'contact-your-name',
        label: 'Your Name:',
        placeholder: 'Enter Your Name',
    }),
    contactYourTitle: Object.freeze({
        id: 'contact-your-title',
        label: 'Your Title:',
        placeholder: 'Enter your title (e.g. Vice President)',
    }),
    contactYourBusinessWebsite: Object.freeze({
        id: 'contact-your-business-website',
        label: 'Business Website (e.g. a page that lists your name and title):',
        placeholder:
            'Enter the URL for a business website that lists your name and title',
    }),
    contactBusinessWebsite: Object.freeze({
        id: 'business-website',
        label:
            'Business Website (e.g. a page that lists the production location’s name and address): ',
        placeholder: 'Enter the URL for the production location’s website',
    }),
    contactBusinessLinkedinProfile: Object.freeze({
        id: 'business-linkedin-profile',
        label: 'Business LinkedIn Profile:',
        placeholder: 'Enter the URL for the business’s LinkedIn profile',
    }),
    yourAdditionalDocumentationTitle: Object.freeze({
        id: 'your-additional-documentation-title',
        label: 'Additional Documentation:',
    }),
    businessAdditionalDocumentationTitle: Object.freeze({
        id: 'business-additional-documentation-title',
        label:
            'Additional Documentation (e.g. utility bill, business registration document):',
    }),
    additionalDocumentationSub: Object.freeze({
        id: 'additional-documentation-sub',
        label:
            'Documentation is only used by our internal team to confirm information about your production location; these documents will never be shared externally.',
    }),
});

export const claimAFacilityAdditionalDataFormFields = Object.freeze({
    sectorsForm: Object.freeze({
        id: 'sectors',
        label: 'Sector(s)',
        placeholder: 'Select',
    }),
    sectorsDecs: Object.freeze({
        id: 'sectors-desc',
        label:
            'Select or enter the sector(s) that this location operates in; e.g.: “Apparel”,”Electronics”,”Renewable Energy”.',
    }),
    numberOfWorkersForm: Object.freeze({
        id: 'number-of-workers',
        label: 'Number of Workers',
        placeholder: 'Enter the number of workers as a number or range',
    }),
    numberOfWorkersDesc: Object.freeze({
        id: 'number-of-workers-desc',
        label:
            'Enter a number or a range for the number of people employed at the location; e.g.: “100”, “100-150”.',
    }),
    localLanguageNameForm: Object.freeze({
        id: 'local-language-name',
        label: 'Local Language Name',
        placeholder:
            'Enter the production location’s name in the local language',
    }),
    localLanguageNameDesc: Object.freeze({
        id: 'local-language-name-desc',
        label:
            'Enter the name of the production location in the language that is spoken in the local area.',
    }),
});

export const freeEmissionsEstimateFormFields = Object.freeze({
    title: Object.freeze({
        label: '🌍 Free Emissions Estimates',
    }),
    description: Object.freeze({
        label:
            'Complete these fields and Open Supply Hub will partner with Climate TRACE to provide you with a free emissions estimate for this location.',
    }),
    openingDateForm: Object.freeze({
        id: 'opening-date',
        label: 'Opening Date',
        placeholder: 'Select year',
    }),
    closingDateForm: Object.freeze({
        id: 'closing-date',
        label: 'Closing Date',
        placeholder: 'Select month/year',
    }),
    annualThroughputForm: Object.freeze({
        id: 'annual-throughput',
        label: 'Estimated Annual Throughput',
        placeholder: 'e.g., 10,000 kg/year',
    }),
    energyConsumptionLabel: Object.freeze({
        label: 'Actual Annual Energy Consumption',
    }),
    energySources: Object.freeze({
        coal: Object.freeze({
            id: 'energy-coal',
            label: 'Coal',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        naturalGas: Object.freeze({
            id: 'energy-natural-gas',
            label: 'Natural Gas',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        diesel: Object.freeze({
            id: 'energy-diesel',
            label: 'Diesel',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        kerosene: Object.freeze({
            id: 'energy-kerosene',
            label: 'Kerosene',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        biomass: Object.freeze({
            id: 'energy-biomass',
            label: 'Biomass',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        charcoal: Object.freeze({
            id: 'energy-charcoal',
            label: 'Charcoal',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        animalWaste: Object.freeze({
            id: 'energy-animal-waste',
            label: 'Animal Waste',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
        electricity: Object.freeze({
            id: 'energy-electricity',
            label: 'Electricity',
            unit: 'MWh',
            placeholder: 'Enter value in MWh',
        }),
        other: Object.freeze({
            id: 'energy-other',
            label: 'Other',
            unit: 'J',
            placeholder: 'Enter value in J',
        }),
    }),
});

export const GRID_COLOR_RAMP = Object.freeze([
    [0, '#C0EBC7'],
    [10, '#81D690'],
    [40, '#4A9957'],
    [160, '#19331D'],
]);

export const OARFont = "'Darker Grotesque',sans-serif";
export const OARColor = '#8428FA';
export const SelectedMarkerColor = '#FFCF3F';
export const OARActionColor = '#FFCF3F';
export const OARSecondaryColor = '#FFA6D0';

// A CSS size value that is used to set a lower bound on the iframe height
// when the width is set to 100%
export const minimum100PercentWidthEmbedHeight = '500px';

export const DONATE_LINK = 'https://givebutter.com/opensupplyhub2022';

export const OS_HUB_BLOG_LINK = 'https://blog.opensupplyhub.org';

export const NavbarItems = [
    {
        type: 'link',
        label: 'Explore',
        href: '/',
        internal: true,
    },
    {
        type: 'submenu',
        label: 'How It Works',
        columns: [
            [
                {
                    label: 'What is OS Hub?',
                    items: [
                        {
                            type: 'button',
                            label: 'Introduction',
                            href: InfoLink,
                        },
                        {
                            type: 'button',
                            label: 'FAQs',
                            href: `${InfoLink}/${InfoPaths.faqs}`,
                        },
                        {
                            type: 'button',
                            label: 'Blog',
                            href: OS_HUB_BLOG_LINK,
                        },
                    ],
                },
            ],
            [
                {
                    label: 'Who is it for?',
                    items: [
                        {
                            type: 'link',
                            label: 'Brands & Retailers',
                            href: `${InfoLink}/${InfoPaths.brands}`,
                        },
                        {
                            type: 'link',
                            label: 'Civil Society',
                            href: `${InfoLink}/${InfoPaths.civilSociety}`,
                        },
                        {
                            type: 'link',
                            label: 'Facilities',
                            href: `${InfoLink}/${InfoPaths.facilities}`,
                        },
                        {
                            type: 'link',
                            label: 'Multi-Stakeholder Initiatives',
                            href: `${InfoLink}/${InfoPaths.multiStakeholderInitiatives}`,
                        },
                        {
                            type: 'link',
                            label: 'Researchers',
                            href: `${InfoLink}/${InfoPaths.researchers}`,
                        },
                        {
                            type: 'link',
                            label: 'Service Providers',
                            href: `${InfoLink}/${InfoPaths.serviceProviders}`,
                        },
                    ],
                },
            ],
            [
                {
                    label: 'What does it cover?',
                    items: [
                        {
                            type: 'link',
                            label: 'Sectors',
                            href: `${InfoLink}/${InfoPaths.sectors}`,
                        },
                    ],
                },
                {
                    label: 'Resources',
                    items: [
                        {
                            type: 'link',
                            label: 'Full Resource Library',
                            href: `${InfoLink}/${InfoPaths.resources}`,
                        },
                        {
                            type: 'link',
                            label: 'Case Studies',
                            href:
                                `${InfoLink}/${InfoPaths.resources}` +
                                `?contentTypes=${InfoResourcesQuery.caseStudy}`,
                        },
                        {
                            type: 'link',
                            label: 'Guides',
                            href:
                                `${InfoLink}/${InfoPaths.resources}` +
                                `?contentTypes=${InfoResourcesQuery.guide}`,
                        },
                        {
                            type: 'link',
                            label: 'Videos',
                            href:
                                `${InfoLink}/${InfoPaths.resources}` +
                                `?contentTypes=${InfoResourcesQuery.video}`,
                        },
                    ],
                },
            ],
            [
                {
                    label: 'The Technology',
                    items: [
                        {
                            type: 'link',
                            label: 'Overview',
                            href: `${InfoLink}/${InfoPaths.technology}`,
                        },
                        {
                            type: 'link',
                            label: 'Developer Resources',
                            href: `${InfoLink}/${InfoPaths.developerResources}`,
                        },
                    ],
                },
                {
                    label: 'Premium Features',
                    items: [
                        {
                            type: 'link',
                            label: 'API',
                            href: `${InfoLink}/${InfoPaths.api}`,
                        },
                        {
                            type: 'link',
                            label: 'Data Cleaning Service',
                            href: `${InfoLink}/${InfoPaths.dataCleaningService}`,
                        },
                        {
                            type: 'link',
                            label: 'Embedded Map',
                            href: `${InfoLink}/${InfoPaths.embeddedMap}`,
                        },
                    ],
                },
            ],
        ],
    },
    {
        type: 'submenu',
        label: 'About Us',
        columns: [
            [
                {
                    label: 'Organization',
                    items: [
                        {
                            type: 'link',
                            label: 'Mission',
                            href: `${InfoLink}/${InfoPaths.mission}`,
                        },
                        {
                            type: 'link',
                            label: 'Supporters',
                            href: `${InfoLink}/${InfoPaths.supporters}`,
                        },
                        {
                            type: 'link',
                            label: 'Press',
                            href: `${InfoLink}/${InfoPaths.press}`,
                        },
                        {
                            type: 'link',
                            label: 'Financials',
                            href: `${InfoLink}/${InfoPaths.financials}`,
                        },
                        {
                            type: 'link',
                            label: 'Governance & Policies',
                            href: `${InfoLink}/${InfoPaths.governanceAndPolicies}`,
                        },
                    ],
                },
            ],
            [
                {
                    label: 'People',
                    items: [
                        {
                            type: 'link',
                            label: 'Team',
                            href: `${InfoLink}/${InfoPaths.team}`,
                        },
                        {
                            type: 'link',
                            label: 'Board of Directors',
                            href: `${InfoLink}/${InfoPaths.boardOfDirectors}`,
                        },
                        {
                            type: 'link',
                            label: 'Work with Us',
                            href: `${InfoLink}/${InfoPaths.workWithUs}`,
                        },
                    ],
                },
            ],
            [
                {
                    label: 'Connect',
                    items: [
                        {
                            type: 'link',
                            label: 'Contact Us',
                            href: `${InfoLink}/${InfoPaths.contactUs}`,
                        },
                        {
                            type: 'button',
                            label: 'Donate',
                            href: DONATE_LINK,
                        },
                    ],
                },
            ],
        ],
    },
    {
        type: 'link',
        label: 'Pricing',
        href: `${InfoLink}/${InfoPaths.pricing}`,
    },
    { type: 'international' },
    { type: 'auth' },
    {
        type: 'button',
        label: 'Add Data',
        href: '/contribute',
        internal: true,
    },
];

// Move the Upload to the front of the list
export const MobileNavbarItems = [
    NavbarItems[NavbarItems.length - 1],
    ...NavbarItems.slice(0, -1),
];

export const EmbeddedMapInfoLink = `${InfoLink}/${InfoPaths.embeddedMap}`;

export const FooterLinks = [
    { label: 'Donate', href: DONATE_LINK },
    {
        label: 'Subscribe',
        href: 'https://share.hsforms.com/1bQwXClZUTjihXk3wt1SX2Abujql',
    },
    { label: 'FAQs', href: `${InfoLink}/${InfoPaths.faqs}` },
    { label: 'Careers', href: `${InfoLink}/work-with-us` },
    { label: 'Media Hub', href: `${InfoLink}/${InfoPaths.mediaHub}` },
    { label: 'Blog', href: OS_HUB_BLOG_LINK },
    {
        label: 'Terms of Service',
        href: `${InfoLink}/${InfoPaths.termsOfService}`,
    },
    { label: 'Privacy Policy', href: `${InfoLink}/${InfoPaths.privacyPolicy}` },
    { label: 'Reporting Line', href: 'https://opensupplyhub.allvoices.co/' },
    { label: 'Contact Us', href: `${InfoLink}/${InfoPaths.contactUs}` },
];

export const SocialMediaLinks = [
    {
        label: 'LinkedIn',
        Icon: () => (
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 20 20"
            >
                <path
                    d="M4.477 19.996H.33V6.646h4.147v13.35ZM2.4 4.825C1.076 4.825 0 3.727 0 2.4a2.402 2.402 0 0 1 4.802 0c0 1.326-1.075 2.424-2.4 2.424Zm17.595 15.17h-4.138v-6.498c0-1.549-.031-3.535-2.156-3.535-2.155 0-2.486 1.683-2.486 3.423v6.61H7.074V6.646h3.977v1.822h.058c.554-1.049 1.906-2.156 3.923-2.156 4.196 0 4.968 2.763 4.968 6.351v7.334h-.004Z"
                    fill="#FFF"
                    fillRule="nonzero"
                />
            </svg>
        ),
        href: 'https://www.linkedin.com/company/open-supply-hub/',
    },
    {
        label: 'YouTube',
        Icon: () => (
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="27"
                height="19"
                viewBox="0 0 27 19"
            >
                <path
                    d="M2.932.583c4.39-.916 19.522-.62 21.084-.017A3.379 3.379 0 0 1 26.4 2.95c.823 3.318.769 9.591.017 12.961a3.379 3.379 0 0 1-2.385 2.385c-3.283.812-17.99.712-21.084 0a3.379 3.379 0 0 1-2.385-2.385C-.212 12.75-.158 6.062.547 2.968A3.379 3.379 0 0 1 2.932.583Zm7.95 4.804v8.088l7.05-4.044-7.05-4.044Z"
                    fill="#FFF"
                    fillRule="nonzero"
                />
            </svg>
        ),
        href: 'https://www.youtube.com/channel/UCy-66mcBwX2wlUM6kvKUrGw',
    },
    {
        label: 'Github',
        Icon: () => (
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="22"
                height="22"
                viewBox="0 0 22 22"
            >
                <path
                    d="M11 0C4.923 0 0 4.923 0 11c0 4.867 3.149 8.979 7.521 10.436.55.096.756-.233.756-.522 0-.262-.013-1.128-.013-2.049-2.764.509-3.479-.674-3.699-1.292-.124-.317-.66-1.293-1.128-1.554-.384-.206-.934-.715-.013-.729.866-.014 1.485.797 1.691 1.128.99 1.663 2.571 1.196 3.204.907.096-.715.385-1.196.701-1.471-2.447-.275-5.005-1.224-5.005-5.431 0-1.197.426-2.187 1.128-2.957-.11-.275-.495-1.402.11-2.915 0 0 .92-.288 3.024 1.128.88-.248 1.816-.372 2.75-.372.936 0 1.87.124 2.75.372 2.104-1.43 3.025-1.128 3.025-1.128.605 1.513.22 2.64.11 2.915.702.77 1.128 1.747 1.128 2.956 0 4.222-2.571 5.157-5.019 5.432.399.344.743 1.004.743 2.035 0 1.471-.014 2.654-.014 3.025 0 .288.206.632.756.522C18.851 19.98 22 15.854 22 11c0-6.077-4.922-11-11-11Z"
                    fill="#FFF"
                    fillRule="evenodd"
                />
            </svg>
        ),
        href: 'https://github.com/opensupplyhub/open-supply-hub',
    },
];

export const facilityDetailsActions = {
    SUGGEST_AN_EDIT: 'Suggest an Edit',
    REPORT_AS_DUPLICATE: 'Report as Duplicate',
    REPORT_AS_CLOSED: 'Report as Closed',
    REPORT_AS_REOPENED: 'Report as Reopened',
    DISPUTE_CLAIM: 'Dispute Claim',
    CLAIM_FACILITY: 'Claim this production location',
    VIEW_ON_OAR: 'View on Open Supply Hub',
};

export const EXTENDED_FIELD_TYPES = [
    {
        label: 'Parent Company',
        fieldName: 'parent_company',
        formatValue: v => v.contributor_name || v.name || v.raw_value,
    },
    {
        label: 'Processing Type',
        fieldName: 'processing_type',
        formatValue: v => {
            const rawValues = Array.isArray(v.raw_values)
                ? v.raw_values
                : v.raw_values.toString().split('|');
            return v.matched_values.map((val, i) =>
                val[3] !== null ? val[3] : rawValues[i],
            );
        },
    },
    {
        label: 'Facility Type',
        fieldName: 'facility_type',
        formatValue: v =>
            v.matched_values.map(val => val[2]).filter(val => val),
    },
    {
        label: 'Product Type',
        fieldName: 'product_type',
        formatValue: v => v.raw_values,
    },
    {
        label: 'Number of Workers',
        fieldName: 'number_of_workers',
        formatValue: ({ min, max }) =>
            max === min ? `${max}` : `${min}-${max}`,
    },
    {
        label: 'Native Language Name',
        fieldName: 'native_language_name',
        formatValue: v => v,
    },
    {
        label: 'DUNS ID',
        fieldName: 'duns_id',
        formatValue: value => value.raw_value,
    },
    {
        label: 'LEI ID',
        fieldName: 'lei_id',
        formatValue: value => value.raw_value,
    },
    {
        label: 'RBA ID',
        fieldName: 'rba_id',
        formatValue: value => value.raw_value,
    },
    {
        label: 'Parent Company OS ID',
        fieldName: 'parent_company_os_id',
        formatValue: value => value.raw_values,
    },
];

export const ADDITIONAL_IDENTIFIERS = Object.freeze([
    'duns_id',
    'lei_id',
    'rba_id',
]);

export const SILVER_MAP_STYLE = [
    {
        elementType: 'geometry',
        stylers: [
            {
                color: '#f5f5f5',
            },
        ],
    },
    {
        elementType: 'labels.icon',
        stylers: [
            {
                visibility: 'off',
            },
        ],
    },
    {
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#616161',
            },
        ],
    },
    {
        elementType: 'labels.text.stroke',
        stylers: [
            {
                color: '#f5f5f5',
            },
        ],
    },
    {
        featureType: 'administrative.land_parcel',
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#bdbdbd',
            },
        ],
    },
    {
        featureType: 'poi',
        elementType: 'geometry',
        stylers: [
            {
                color: '#eeeeee',
            },
        ],
    },
    {
        featureType: 'poi',
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#757575',
            },
        ],
    },
    {
        featureType: 'poi.park',
        elementType: 'geometry',
        stylers: [
            {
                color: '#e5e5e5',
            },
        ],
    },
    {
        featureType: 'poi.park',
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#9e9e9e',
            },
        ],
    },
    {
        featureType: 'road',
        elementType: 'geometry',
        stylers: [
            {
                color: '#ffffff',
            },
        ],
    },
    {
        featureType: 'road.arterial',
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#757575',
            },
        ],
    },
    {
        featureType: 'road.highway',
        elementType: 'geometry',
        stylers: [
            {
                color: '#dadada',
            },
        ],
    },
    {
        featureType: 'road.highway',
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#616161',
            },
        ],
    },
    {
        featureType: 'road.local',
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#9e9e9e',
            },
        ],
    },
    {
        featureType: 'transit.line',
        elementType: 'geometry',
        stylers: [
            {
                color: '#e5e5e5',
            },
        ],
    },
    {
        featureType: 'transit.station',
        elementType: 'geometry',
        stylers: [
            {
                color: '#eeeeee',
            },
        ],
    },
    {
        featureType: 'water',
        elementType: 'geometry',
        stylers: [
            {
                color: '#c9c9c9',
            },
        ],
    },
    {
        featureType: 'water',
        elementType: 'labels.text.fill',
        stylers: [
            {
                color: '#9e9e9e',
            },
        ],
    },
];

export const EXTENDED_FIELDS_EXPLANATORY_TEXT =
    'These fields were added to OS Hub in March 2022. As more data is contributed, more results will become available.';

export const optionsForSortingResults = [
    { value: 'name_asc', label: 'A to Z' },
    { value: 'name_desc', label: 'Z to A' },
    {
        value: 'contributors_desc',
        label: (
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                    justifyContent: 'start',
                    alignItems: 'center',
                }}
            >
                <span style={{ paddingRight: '3px' }}># Contributors</span>
                <ArrowDownwardIcon style={{ fontSize: 20 }} />
            </div>
        ),
    },
    {
        value: 'contributors_asc',
        label: (
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                    justifyContent: 'start',
                    alignItems: 'center',
                }}
            >
                <span style={{ paddingRight: '3px' }}># Contributors</span>
                <ArrowUpwardIcon style={{ fontSize: 20 }} />
            </div>
        ),
    },
];

// This offset is necessary to match row indices in the uploaded files.
export const uploadedFileRowIndexOffset = 2;

export const USER_DEFAULT_STATE = Object.freeze({
    isAnon: true,
    email: null,
    id: null,
    contributor_id: null,
    is_superuser: false,
    is_staff: false,
    is_moderation_mode: false,
    allowed_records_number: FREE_FACILITIES_DOWNLOAD_LIMIT,
});

export const facilityClaimStepsNames = Object.freeze({
    CLAIM_PROD_LOCATION: 'Claim this production location',
    SUPPORT_DOC: 'Support Documentation',
    ADDITIONAL_DATA: 'Additional Data',
});

export const componentsWithErrorMessage = Object.freeze({
    missingListName: 'Missing required Facility List Name.',
    invalidCharacters: (
        <>
            The <b>List Name</b> you entered contains invalid characters.
            Allowed characters include: letters, numbers, spaces, apostrophe (
            &#39; ), comma ( &#44; ), hyphen ( &#45; ), ampersand ( &#38; ),
            period ( &#46; ), parentheses ( ), and square brackets ( &#91;&#93;
            ). Characters that contain accents are not allowed.
        </>
    ),
    mustConsistOfLetters: 'Facility List Name must also consist of letters.',
    missingFile: 'Missing required Facility List File.',
});

export const OS_ID_LENGTH = 15;

/*
This object maps specific list parsing error types to user-friendly error
messages.
Each key in the object corresponds to an error type that may occur during
the parsing of lists. The values are either React components or strings
that provide detailed feedback to the user, including guidance on how to
resolve the issue.
 */
export const listParsingErrorMappings = {
    RequiredFieldsMissingError: (
        <>
            One or more required columns are missing or incorrectly formatted.
            Please ensure you upload your data{' '}
            <a
                href="https://info.opensupplyhub.org/resources/preparing-data"
                target="_blank"
                rel="noreferrer"
            >
                using OS Hub’s template
            </a>
            , without altering the column headers.
        </>
    ),
};

export const DATA_SOURCES_ENUM = Object.freeze({
    API: 'API',
    SLC: 'SLC',
});

export const MODERATION_STATUSES_ENUM = Object.freeze({
    PENDING: 'PENDING',
    APPROVED: 'APPROVED',
    REJECTED: 'REJECTED',
});

export const PRODUCTION_LOCATION_CLAIM_STATUSES_ENUM = Object.freeze({
    CLAIMED: 'claimed',
    UNCLAIMED: 'unclaimed',
    PENDING: 'pending',
});

export const MODERATION_ACTIONS_ENUM = Object.freeze({
    NEW_LOCATION: 'NEW_LOCATION',
    MATCHED: 'MATCHED',
    REJECTED: 'REJECTED',
});

export const MODERATION_QUEUE_HEAD_CELLS = Object.freeze([
    { id: 'created_at', label: 'Created Date' },
    { id: 'name', label: 'Location Name' },
    { id: 'country', label: 'Country' },
    { id: 'contributor_name', label: 'Contributor' },
    { id: 'source', label: 'Source Type' },
    { id: 'status', label: 'Moderation Status' },
    { id: 'status_change_date', label: 'Moderation Decision Date' },
    { id: 'updated_at', label: 'Last Updated' },
]);

export const DATE_FORMATS = Object.freeze({
    SHORT: 'L',
    LONG: 'LL',
    LONG_WITH_TIME: 'LLL',
    FULL: 'LLLL',
});

export const MODERATION_QUEUE = 'ModerationQueue';

export const MODERATION_STATUS_COLORS = Object.freeze({
    [MODERATION_STATUSES_ENUM.PENDING]: COLOURS.PALE_LIGHT_YELLOW,
    [MODERATION_STATUSES_ENUM.APPROVED]: COLOURS.MINT_GREEN,
    [MODERATION_STATUSES_ENUM.REJECTED]: COLOURS.LIGHT_RED,
});

export const MODERATION_INITIAL_PAGE_INDEX = 0;
export const MODERATION_DEFAULT_ROWS_PER_PAGE = 25;

export const MAINTENANCE_MESSAGE =
    'Open Supply Hub is undergoing maintenance and not accepting new data at the moment. Please try again in a few minutes.';

export const mockedSectors = [
    ['Electronics', 'Electronics'],
    ['Accommodation', 'Accommodation'],
    ['Aerospace', 'Aerospace'],
    ['Agriculture', 'Agriculture'],
    ['Air Transportation', 'Air Transportation'],
    ['Allied Products', 'Allied Products'],
    ['Animal Production', 'Animal Production'],
    ['Apparel', 'Apparel'],
    ['Apparel Accessories', 'Apparel Accessories'],
    ['Appliances', 'Appliances'],
    ['Aquaculture', 'Aquaculture'],
    ['Archives', 'Archives'],
    ['Arts', 'Arts'],
    ['Arts & Entertainment', 'Arts & Entertainment'],
    ['Automotive', 'Automotive'],
    ['Automotive Parts', 'Automotive Parts'],
    ['Banking', 'Banking'],
    ['Beauty Products', 'Beauty Products'],
    ['Beverages', 'Beverages'],
    ['Biotechnology', 'Biotechnology'],
    ['Books', 'Books'],
    ['Building Construction', 'Building Construction'],
    ['Building Materials', 'Building Materials'],
    ['Chemicals', 'Chemicals'],
    ['Civics', 'Civics'],
    ['Civil Engineering Construction', 'Civil Engineering Construction'],
    ['Coal', 'Coal'],
    ['Commodities', 'Commodities'],
    ['Components', 'Components'],
    ['Computers', 'Computers'],
    ['Computing Infrastructure', 'Computing Infrastructure'],
    ['Construction', 'Construction'],
    ['Consumer Products', 'Consumer Products'],
    ['Crop Production', 'Crop Production'],
    ['Durable Goods', 'Durable Goods'],
    ['Educational Services', 'Educational Services'],
    ['Electrical Devices', 'Electrical Devices'],
    ['Electricity', 'Electricity'],
    ['Electronic Product Manufacturing', 'Electronic Product Manufacturing'],
    ['Energy', 'Energy'],
    ['Energy Production & Utilities', 'Energy Production & Utilities'],
    ['Entertainment', 'Entertainment'],
    ['Equipment', 'Equipment'],
    ['Farming', 'Farming'],
    ['Finance', 'Finance'],
    ['Financial Services', 'Financial Services'],
    ['Fishing', 'Fishing'],
    ['Food', 'Food'],
    ['Food & Beverage', 'Food & Beverage'],
    ['Food Industry', 'Food Industry'],
    ['Food Manufacturing', 'Food Manufacturing'],
    ['Footwear', 'Footwear'],
    ['Forestry', 'Forestry'],
    ['Furniture', 'Furniture'],
    ['Garden Tools', 'Garden Tools'],
    ['Gas', 'Gas'],
    ['General Merchandise', 'General Merchandise'],
    ['Ground Passenger Transportation', 'Ground Passenger Transportation'],
    ['Hard Goods', 'Hard Goods'],
    ['Health', 'Health'],
    ['Healthcare', 'Healthcare'],
    ['Hobby', 'Hobby'],
    ['Home Accessories', 'Home Accessories'],
    ['Home Furnishings', 'Home Furnishings'],
    ['Hospitals', 'Hospitals'],
    ['Home Textiles', 'Home Textiles'],
    ['Hunting', 'Hunting'],
    ['Information', 'Information'],
    ['International Affairs', 'International Affairs'],
    ['Jewelry', 'Jewelry'],
    ['Leather', 'Leather'],
    ['Logging', 'Logging'],
    ['Machinery Manufacturing', 'Machinery Manufacturing'],
    ['Maintenance', 'Maintenance'],
    ['Manufacturing', 'Manufacturing'],
    ['Material Production', 'Material Production'],
    ['Medical Equipment & Services', 'Medical Equipment & Services'],
    ['Merchant Wholesalers', 'Merchant Wholesalers'],
    ['Metal Manufacturing', 'Metal Manufacturing'],
    ['Mining', 'Mining'],
    ['Multi-Category', 'Multi-Category'],
    ['Musical Instruments', 'Musical Instruments'],
    ['Nondurable Goods', 'Nondurable Goods'],
    ['Nursing', 'Nursing'],
    ['Oil & Gas', 'Oil & Gas'],
    ['Paper Products', 'Paper Products'],
    ['Parts Dealers', 'Parts Dealers'],
    ['Personal Care Products', 'Personal Care Products'],
    ['Pharmaceuticals', 'Pharmaceuticals'],
    ['Pipeline Transportation', 'Pipeline Transportation'],
    ['Plastics', 'Plastics'],
    ['Printing', 'Printing'],
    ['Professional Services', 'Professional Services'],
    ['Quarrying', 'Quarrying'],
    ['Rail Transportation', 'Rail Transportation'],
    ['Recreation', 'Recreation'],
    ['Renewable Energy', 'Renewable Energy'],
    ['Renting', 'Renting'],
    ['Repair', 'Repair'],
    ['Rubber Products', 'Rubber Products'],
    ['Solar Energy', 'Solar Energy'],
    ['Research', 'Research'],
    ['Specialty Trade Contractors', 'Specialty Trade Contractors'],
    ['Sports Equipment', 'Sports Equipment'],
    ['Sporting Goods', 'Sporting Goods'],
    ['Storage', 'Storage'],
    ['Supplies Dealers', 'Supplies Dealers'],
    ['Technical Services', 'Technical Services'],
    ['Technology', 'Technology'],
    ['Telecommunications', 'Telecommunications'],
    ['Textiles', 'Textiles'],
    ['Tobacco Products', 'Tobacco Products'],
    ['Toys', 'Toys'],
    ['Transportation Equipment', 'Transportation Equipment'],
    ['Trucking', 'Trucking'],
    ['Utilities', 'Utilities'],
    ['Water Utilities', 'Water Utilities'],
    ['Warehousing', 'Warehousing'],
    ['Wholesale Trade', 'Wholesale Trade'],
    ['Wood Products', 'Wood Products'],
    ['Consumer Electronics', 'Consumer Electronics'],
    ['Home', 'Home'],
    ['Maritime Transportation', 'Maritime Transportation'],
    [
        'Technical and Scientific Activities',
        'Technical and Scientific Activities',
    ],
    ['Waste Management', 'Waste Management'],
    ['Recycling', 'Recycling'],
    ['Pets', 'Pets'],
    ['Packaging', 'Packaging'],
];

export const MAX_LOCATIONS_TO_SHOW = 100;

export const SLC_FORM_CONSTRAINTS = Object.freeze({
    MAX_PRODUCT_TYPE_COUNT: 50,
    MAX_STRING_LENGTH: 200,
});

export const HEADER_HEIGHT = 116;

export const API_V1_ERROR_REQUEST_SOURCE_ENUM = {
    CLIENT: 'CLIENT',
    SERVER: 'SERVER',
};
