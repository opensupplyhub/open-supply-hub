import {
    array,
    arrayOf,
    bool,
    func,
    number,
    oneOf,
    oneOfType,
    shape,
    string,
} from 'prop-types';
import mapValues from 'lodash/mapValues';
import omitBy from 'lodash/omitBy';
import includes from 'lodash/includes';
import partial from 'lodash/partial';

import {
    registrationFieldsEnum,
    profileFieldsEnum,
    facilityListItemStatusChoicesEnum,
    ALLOW_LARGE_DOWNLOADS,
    FEATURE,
    FEATURE_COLLECTION,
    POINT,
    facilityMatchStatusChoicesEnum,
    CLAIM_A_FACILITY,
    VECTOR_TILE,
    REPORT_A_FACILITY,
    EMBEDDED_MAP_FLAG,
    EXTENDED_PROFILE_FLAG,
    DISABLE_LIST_UPLOADING,
    facilityClaimStatusChoicesEnum,
    SHOW_ADDITIONAL_IDENTIFIERS,
} from './constants';

export const registrationFormValuesPropType = shape({
    [registrationFieldsEnum.email]: string.isRequired,
    [registrationFieldsEnum.name]: string.isRequired,
    [registrationFieldsEnum.description]: string.isRequired,
    [registrationFieldsEnum.website]: string.isRequired,
    [registrationFieldsEnum.contributorType]: string.isRequired,
    [registrationFieldsEnum.otherContributorType]: string.isRequired,
    [registrationFieldsEnum.password]: string.isRequired,
    [registrationFieldsEnum.confirmPassword]: string.isRequired,
    [registrationFieldsEnum.newsletter]: bool.isRequired,
    [registrationFieldsEnum.tos]: bool.isRequired,
});

export const registrationFormInputHandlersPropType = shape(
    Object.values(registrationFieldsEnum).reduce(
        (accumulator, key) =>
            Object.assign({}, accumulator, { [key]: func.isRequired }),
        {},
    ),
);

export const userPropType = shape({
    isAnon: bool.isRequired,
    email: string,
    id: number,
    contributor_id: number,
    is_superuser: bool.isRequired,
    is_staff: bool.isRequired,
    is_moderation_mode: bool.isRequired,
    allowed_records_number: number.isRequired,
    // is_free_limit_active: bool.isRequired,
});

export const profileFormValuesPropType = shape(
    Object.values(profileFieldsEnum).reduce(
        (accumulator, key) =>
            Object.assign({}, accumulator, {
                [key]:
                    key === 'isModerationMode'
                        ? bool.isRequired
                        : string.isRequired,
            }),
        {},
    ),
);

export const profileFormInputHandlersPropType = shape(
    Object.values(profileFieldsEnum).reduce(
        (accumulator, key) =>
            Object.assign({}, accumulator, { [key]: func.isRequired }),
        {},
    ),
);

export const tokenPropType = shape({
    token: string.isRequired,
    created: string.isRequired,
});

export const userApiInfoPropType = shape({
    apiCallAllowance: string.isRequired,
    currentCallCount: number.isRequired,
    renewalPeriod: string.isRequired,
});

export const facilityMatchPropType = shape({
    id: number.isRequired,
    status: oneOf(Object.values(facilityMatchStatusChoicesEnum)).isRquired,
    confidence: number.isRequired,
    os_id: string.isRequired,
    name: string.isRequired,
    address: string.isRequired,
    results: arrayOf(
        shape({
            version: number.isRequired,
            match_type: string.isRequired,
        }),
    ),
});

export const facilityListItemPropType = shape({
    id: number.isRequired,
    row_index: number.isRequired,
    raw_data: string.isRequired,
    status: oneOf(Object.values(facilityListItemStatusChoicesEnum)).isRequired,
    processing_started_at: string,
    processing_completed_at: string,
    name: string.isRequired,
    address: string.isRequired,
    country_code: string.isRequired,
    country_name: string.isRequired,
    geocoded_point: string,
    geocoded_address: string,
    processing_errors: arrayOf(string.isRequired),
    matched_facility: shape({
        os_id: string.isRequired,
        address: string.isRequired,
        name: string.isRequired,
        created_from_id: number.isRequired,
        location: shape({
            lng: number.isRequired,
            lat: number.isRequired,
        }).isRequired,
    }),
    matches: arrayOf(
        shape({
            id: number.isRequired,
            os_id: string.isRequired,
            address: string.isRequired,
            name: string.isRequired,
            location: shape({
                lng: number.isRequired,
                lat: number.isRequired,
            }).isRequired,
        }).isRequired,
    ),
});

export const listParsingErrorPropType = shape({
    message: string.isRequired,
    type: string.isRequired,
});

export const facilityListPropType = shape({
    id: number.isRequired,
    name: string,
    description: string,
    contributor_id: number,
    file_name: string.isRequired,
    is_active: bool.isRequired,
    is_public: bool.isRequired,
    item_count: number.isRequired,
    items_url: string.isRequired,
    statuses: arrayOf(oneOf(Object.values(facilityListItemStatusChoicesEnum))),
    status_counts: shape(
        mapValues(
            omitBy(
                facilityListItemStatusChoicesEnum,
                partial(includes, [
                    facilityListItemStatusChoicesEnum.NEW_FACILITY,
                    facilityListItemStatusChoicesEnum.REMOVED,
                ]),
            ),
            () => number.isRequired,
        ),
    ).isRequired,
    parsing_errors: arrayOf(listParsingErrorPropType),
    created_at: string.isRequired,
});

export const contributorOptionPropType = shape({
    value: oneOfType([number, string]).isRequired,
    label: string.isRequired,
});

export const contributorOptionsPropType = arrayOf(contributorOptionPropType);

export const contributorTypeOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const contributorListOptionsPropType = arrayOf(string);

export const claimStatusOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const countryOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const sectorOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const groupedSectorOptionsPropType = arrayOf(
    shape({
        label: string.isRequired,
        options: arrayOf(
            shape({
                groupLabel: string.isRequired,
                label: string.isRequired,
                value: string.isRequired,
            }),
        ).isRequired,
    }),
);

export const facilityTypeOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const parentCompanyOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const processingTypeOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const facilityProcessingTypeOptionsPropType = arrayOf(
    shape({
        facilityType: string.isRequired,
        processingTypes: arrayOf(string),
    }),
);

export const productTypeOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const numberOfWorkerOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const moderationStatusOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const dataSourceOptionsPropType = arrayOf(
    shape({
        value: string.isRequired,
        label: string.isRequired,
    }),
);

export const facilityPropType = shape({
    id: string.isRequired,
    type: oneOf([FEATURE]).isRequired,
    geometry: shape({
        type: oneOf([POINT]).isRequired,
        coordinates: arrayOf(number.isRequired).isRequired,
    }).isRequired,
    properties: shape({
        name: string.isRequired,
        address: string.isRequired,
        country_code: string.isRequired,
        country_name: string.isRequired,
    }).isRequired,
});

export const facilityDetailsContributorPropType = shape({
    id: number,
    name: string.isRequired,
    is_verified: bool,
});

export const facilityDetailsPropType = shape({
    id: string.isRequired,
    type: oneOf([FEATURE]).isRequired,
    geometry: shape({
        type: oneOf([POINT]).isRequired,
        coordinates: arrayOf(number.isRequired).isRequired,
    }).isRequired,
    properties: shape({
        name: string.isRequired,
        address: string.isRequired,
        country_code: string.isRequired,
        country_name: string.isRequired,
        other_names: arrayOf(string),
        other_addresses: arrayOf(string),
        contributors: arrayOf(facilityDetailsContributorPropType),
    }).isRequired,
});

export const facilityCollectionPropType = shape({
    type: oneOf([FEATURE_COLLECTION]).isRequired,
    features: arrayOf(facilityPropType).isRequired,
});

export const reactSelectOptionPropType = shape({
    value: oneOfType([number, string]).isRequired,
    label: string.isRequired,
});

export const filtersPropType = shape({
    facilityFreeTextQuery: string.isRequired,
    contributors: arrayOf(reactSelectOptionPropType).isRequired,
    contributorTypes: arrayOf(reactSelectOptionPropType).isRequired,
    countries: arrayOf(reactSelectOptionPropType).isRequired,
    sectors: arrayOf(reactSelectOptionPropType).isRequired,
    combineContributors: string.isRequired,
});

export const facilityListItemStatusPropType = oneOf(
    Object.values(facilityListItemStatusChoicesEnum).concat('Status'),
);

export const featureFlagPropType = oneOf([
    CLAIM_A_FACILITY,
    VECTOR_TILE,
    REPORT_A_FACILITY,
    EMBEDDED_MAP_FLAG,
    EXTENDED_PROFILE_FLAG,
    ALLOW_LARGE_DOWNLOADS,
    DISABLE_LIST_UPLOADING,
    SHOW_ADDITIONAL_IDENTIFIERS,
]);

export const facilityClaimsListPropType = arrayOf(
    shape({
        created_at: string.isRequired,
        updated_at: string.isRequired,
        id: number.isRequired,
        os_id: string.isRequired,
        facility_name: string.isRequired,
        contributor_id: number.isRequired,
        contributor_name: string.isRequired,
        facility_country_name: string.isRequired,
        status: oneOf(Object.values(facilityClaimStatusChoicesEnum)).isRequired,
        claim_decision: string.isReqired,
    }).isRequired,
);

export const facilityClaimNotePropType = shape({
    id: number.isRequired,
    created_at: string.isRequired,
    updated_at: string.isRequired,
    note: string.isRequired,
});

const attachmentPropTypes = shape({
    file_name: string.isRequired,
    claim_attachment: string.isRequired,
});

export const facilityClaimAttachmentsPropType = oneOfType([
    arrayOf(attachmentPropTypes),
    array,
]);

export const facilityClaimPropType = shape({
    id: number.isRequired,
    created_at: string.isRequired,
    updated_at: string.isRequired,
    contact_person: string.isRequired,
    job_title: string.isRequired,
    email: string.isRequired,
    company_name: string.isRequired,
    website: string.isRequired,
    facility_description: string.isRequired,
    linkedin_profile: string.isRequired,
    status: oneOf(Object.values(facilityClaimStatusChoicesEnum)).isRequired,
    contributor: shape({}).isRequired,
    facility: facilityPropType.isRequired,
    facility_website: string.isRequired,
    sector: oneOfType([arrayOf(string), oneOf([null])]),
    facility_workers_count: oneOfType([string, oneOf([null])]),
    facility_name_native_language: string.isRequired,
    status_change: shape({
        status_change_by: string,
        status_change_date: string,
        status_change_reason: string,
    }).isRequired,
    notes: arrayOf(facilityClaimNotePropType).isRequired,
    attachments: facilityClaimAttachmentsPropType.isRequired,
});

export const approvedFacilityClaimPropType = shape({
    id: number.isRequired,
    facility_description: string.isRequired,
    facility_name_english: string.isRequired,
    facility_name_native_language: string.isRequired,
    facility_address: string.isRequired,
    facility_phone_number: string.isRequired,
    facility_phone_number_publicly_visible: bool.isRequired,
    facility_website: string.isRequired,
    facility_website_publicly_visible: bool.isRequired,
    facility_minimum_order_quantity: string.isRequired,
    facility_average_lead_time: string.isRequired,
    facility_workers_count: oneOfType([number, string]).isRequired,
    facility_female_workers_percentage: oneOfType([number, string]).isRequired,
    point_of_contact_person_name: string.isRequired,
    point_of_contact_email: string.isRequired,
    point_of_contact_publicly_visible: bool.isRequired,
    office_official_name: string.isRequired,
    office_country_code: string.isRequired,
    office_phone_number: string.isRequired,
    office_info_publicly_visible: bool.isRequired,
    facility: facilityDetailsPropType.isRequired,
    facility_type: arrayOf(arrayOf(string)).isRequired,
    facility_types: arrayOf(arrayOf(string)).isRequired,
    affiliation_choices: arrayOf(arrayOf(string)).isRequired,
    certification_choices: arrayOf(arrayOf(string)).isRequired,
    production_type_choices: arrayOf(arrayOf(string)).isRequired,
});

export const apiBlockPropType = shape({
    limit: number.isRequired,
    actual: number.isRequired,
    contributor: string.isRequired,
    active: bool.isRequired,
    grace_limit: number,
    grace_reason: string,
    until: string.isRequired,
    created_at: string.isReqired,
});

export const activityReportPropType = shape({
    approved_at: string,
    closure_state: string.isRequired,
    created_at: string.isRequired,
    facility: string.isRequired,
    facility_name: string.isRequired,
    id: number.isRequired,
    reason_for_report: string.isRequired,
    reported_by_contributor: string.isRequired,
    reported_by_user: string.isRequired,
    status: string.isRequired,
    status_change_by: string,
    status_change_date: string,
    status_change_reason: string,
    updated_at: string.isRequired,
});

export const filterOptionsPropType = shape({
    data: arrayOf(
        shape({
            value: string.isRequired,
            label: string.isRequired,
        }),
    ),
    error: oneOfType([string, oneOf([null])]),
    fetching: bool.isRequired,
});

export const productionLocationCountryPropType = shape({
    alpha_2: string.isRequired,
    alpha_3: string.isRequired,
    name: string.isRequired,
    numeric: string.isRequired,
});

export const productionLocationPropType = shape({
    os_id: string,
    name: string,
    address: string,
    country: productionLocationCountryPropType,
    historical_os_id: arrayOf(string),
});

export const moderationEventsListItemPropType = shape({
    moderation_id: string,
    created_at: string,
    updated_at: string,
    os_id: string,
    cleaned_data: shape({
        name: string,
        address: string,
        country: productionLocationCountryPropType,
    }),
    contributor_id: number,
    contributor_name: string,
    request_type: string,
    source: string,
    status: oneOf(['PENDING', 'APPROVED', 'REJECTED']),
    status_change_date: string,
    claim_id: number,
});

export const moderationEventsListPropType = arrayOf(
    moderationEventsListItemPropType,
);

export const potentialMatchesPropType = arrayOf(
    shape({
        os_id: string.isRequired,
        name: string.isRequired,
        address: string.isRequired,
        sector: arrayOf(string),
        parent_company: string,
        product_type: arrayOf(string),
        location_type: arrayOf(string),
        processing_type: arrayOf(string),
        number_of_workers: shape({
            min: number.isRequired,
            max: number.isRequired,
        }),
        coordinates: shape({
            lat: number.isRequired,
            lng: number.isRequired,
        }),
        local_name: string,
        description: string,
        business_url: string,
        minimum_order_quantity: string,
        average_lead_time: string,
        percent_female_workers: number,
        affiliations: arrayOf(string),
        certifications_standards_regulations: arrayOf(string),
        historical_os_id: arrayOf(string),
        country: productionLocationCountryPropType.isRequired,
        claim_status: string,
    }),
);
