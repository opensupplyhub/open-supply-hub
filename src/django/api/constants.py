class FileHeaderField:
    COUNTRY = 'country'
    NAME = 'name'
    ADDRESS = 'address'
    LAT = 'lat'
    LNG = 'lng'


class ProcessingAction:
    PARSE = 'parse'
    GEOCODE = 'geocode'
    MATCH = 'match'
    SUBMIT_JOB = 'submitjob'
    CONFIRM = 'confirm'
    DELETE_FACILITY = 'delete_facility'
    PROMOTE_MATCH = 'promote_match'
    MERGE_FACILITY = 'merge_facility'
    SPLIT_FACILITY = 'split_facility'
    MOVE_FACILITY = 'move_facility'
    NOTIFY_COMPLETE = 'notify_complete'
    ITEM_REMOVED = 'item_removed'
    UNDO_MERGE = 'undo_merge'


class FacilitiesQueryParams:
    Q = 'q'
    ID = 'id'
    NAME = 'name'
    CONTRIBUTORS = 'contributors'
    LISTS = 'lists'
    CONTRIBUTOR_TYPES = 'contributor_types'
    COUNTRIES = 'countries'
    COMBINE_CONTRIBUTORS = 'combine_contributors'
    BOUNDARY = 'boundary'
    EMBED = 'embed'
    PARENT_COMPANY = 'parent_company'
    FACILITY_TYPE = 'facility_type'
    PROCESSING_TYPE = 'processing_type'
    PRODUCT_TYPE = 'product_type'
    NUMBER_OF_WORKERS = 'number_of_workers'
    NATIVE_LANGUAGE_NAME = 'native_language_name'
    SECTOR = 'sectors'


class FacilityListQueryParams:
    CONTRIBUTOR = 'contributor'
    STATUS = 'status'
    MATCH_RESPONSIBILITY = 'match_responsibility'


class FacilityListItemsQueryParams:
    SEARCH = 'search'
    STATUS = 'status'


class FacilityMergeQueryParams:
    TARGET = 'target'
    MERGE = 'merge'


class FacilityCreateQueryParams:
    CREATE = 'create'
    PUBLIC = 'public'
    TEXT_ONLY_FALLBACK = 'textonlyfallback'


class FeatureGroups:
    CAN_GET_FACILITY_HISTORY = 'can_get_facility_history'
    CAN_SUBMIT_FACILITY = 'can_submit_facility'
    CAN_SUBMIT_PRIVATE_FACILITY = 'can_submit_private_facility'
    CAN_VIEW_FULL_CONTRIB_DETAIL = 'can_view_full_contrib_detail'


class FacilityHistoryActions:
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    MERGE = 'MERGE'
    SPLIT = 'SPLIT'
    MOVE = 'MOVE'
    OTHER = 'OTHER'
    ASSOCIATE = 'ASSOCIATE'
    DISSOCIATE = 'DISSOCIATE'
    CLAIM = 'CLAIM'
    CLAIM_UPDATE = 'CLAIM_UPDATE'
    CLAIM_REVOKE = 'CLAIM_REVOKE'


class FacilityClaimStatuses:
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DENIED = 'DENIED'
    REVOKED = 'REVOKED'


class Affiliations:
    BENEFITS_BUSINESS_WORKERS = 'Benefits for Business and Workers (BBW)'
    BETTER_MILLS_PROGRAM = 'Better Mills Program'
    BETTER_WORK = 'Better Work (ILO)'
    CANOPY = 'Canopy'
    ETHICAL_TRADING_INITIATIVE = 'Ethical Trading Initiative'
    EUROPEAN_OUTDOOR_GROUP = 'European Outdoor Group'
    FAIR_LABOR_ASSOCIATION = 'Fair Labor Association'
    FAIR_WEAR_FOUNDATION = 'Fair Wear Foundation'
    SEDEX = 'SEDEX'
    SOCIAL_LABOR_CONVERGENCE_PLAN = 'Social and Labor Convergence Plan (SLCP)'
    SUSTAINABLE_APPAREL_COALITION = 'Sustainable Apparel Coalition'
    SWEATFREE_PURCHASING_CONSORTIUM = 'Sweatfree Purchasing Consortium'
    HERHEATH = 'HERhealth'
    HERFINANCE = 'HERfinance'
    HERRESPECT = 'HERrespect'
    ZDHC = 'ZDHC'


class Certifications:
    BCI = 'BCI'
    B_CORP = 'B Corp'
    BLUESIGN = 'Bluesign'
    CANOPY = 'Canopy'
    CRADLE_TO_CRADLE = 'Cradle to Cradle'
    EU_ECOLABEL = 'EU Ecolabel'
    FSC = 'FSC'
    GLOBAL_RECYCLING_STANDARD = 'Global Recycling Standard (GRS)'
    GOTS = 'GOTS'
    GREEN_SCREEN = 'Green Screen for Safer Chemicals'
    HIGG_INDEX = 'Higg Index'
    IMO_CONTROL = 'IMO Control'
    INTERNATIONAL_WOOL_TEXTILE = ('International Wool Textile Organisation'
                                  ' (IWTO)')
    ISO_9000 = 'ISO 9000'
    IVN_LEATHER = 'IVN leather'
    LEATHER_WORKING_GROUP = 'Leather Working Group'
    NORDIC_SWAN = 'Nordic Swan'
    OEKO_TEX_STANDARD = 'Oeko-Tex Standard 100'
    OEKO_TEX_STEP = 'Oeko-Tex STeP'
    OEKO_TEX_ECO_PASSPORT = 'Oeko-Tex Eco Passport'
    OEKO_TEX_MADE_IN_GREEN = 'Oeko-Tex Made in Green'
    PEFC = 'PEFC'
    REACH = 'REACH'
    RESPONSIBLE_DOWN_STANDARD = 'Responsible Down Standard (RDS)'
    RESPONSIBLE_WOOL_STANDARD = 'Responsible Wool Standard (RWS)'
    SAB8000 = 'SA8000'
    GREEN_BUTTON = 'Green Button'
    FAIRTRADE_USA = 'Fairtrade USA'


class LogDownloadQueryParams:
    PATH = 'path'
    RECORD_COUNT = 'record_count'


class UpdateLocationParams:
    LAT = 'lat'
    LNG = 'lng'
    NOTES = 'notes'
    CONTRIBUTOR_ID = 'contributor_id'


class DateFormats:
    STANDARD = '%Y-%m-%d %H:%M:%S.%f'
    SECOND = '%Y-%m-%d %H:%M:%S'
    MONTH = '%Y-%m'
    WEEK = '%Y-%W'


class MatchResponsibility:
    MODERATOR = "moderator"
    CONTRIBUTOR = "contributor"

    CHOICES = [
        (MODERATOR, 'OS Hub admins'),
        (CONTRIBUTOR, 'The contributor'),
    ]


class OriginSource:
    OSHUB = "os_hub"
    RBA = "rba"

    CHOICES = [
        (OSHUB, ' OS Hub'),
        (RBA, 'RBA'),
    ]


class NumberOfWorkersRanges:
    STANDARD_RANGES = [{
        'min': 0,
        'max': 1000,
        'label': 'Less than 1000'
    }, {
        'min': 1001,
        'max': 5000,
        'label': '1001-5000'
    }, {
        'min': 5001,
        'max': 10000,
        'label': '5001-10000'
    }, {
        'min': 10001,
        'label': 'More than 10000'
    }]


class APIErrorMessages:
    GEOCODED_NO_RESULTS = 'The address you submitted can not be geocoded.'
    MAINTENANCE_MODE = ('Open Supply Hub is undergoing maintenance and '
                        'not accepting new data at the moment. Please '
                        'try again in a few minutes.')
    TEMPORARILY_UNAVAILABLE = (
        'The endpoint is temporarily unavailable. Please try again later.'
    )


class FacilitiesDownloadSettings:
    FREE_FACILITIES_DOWNLOAD_LIMIT = 5000


class FacilitiesListSettings:
    DEFAULT_PAGE_LIMIT = 100


class CoordinateLimits:
    LAT_MIN = -90
    LAT_MAX = 90
    LNG_MIN = -180
    LNG_MAX = 180


# API v1
class APIV1CommonErrorMessages:
    COMMON_REQ_BODY_ERROR = 'The request body is invalid.'
    COMMON_INTERNAL_ERROR = (
        'An unexpected error occurred while processing the request.'
    )
    COMMON_REQ_QUERY_ERROR = 'The request query is invalid.'
    COMMON_REQ_PARAMETER_ERROR = 'The request parameter is invalid.'
    MAINTENANCE_MODE = (
        'Open Supply Hub is undergoing maintenance and not accepting new data '
        'at the moment. Please try again in a few minutes.'
    )
    LOCATION_NOT_FOUND = 'The location with the given id was not found.'
    LOCATION_ID_NOT_VALID = 'The value must be a valid id.'


class APIV1LocationContributionErrorMessages:
    GEOCODED_NO_RESULTS = (
        'A valid address could not be found for the provided country and '
        'address. This may be due to incorrect, incomplete, or ambiguous '
        'information. Please verify and try again.'
    )

    @staticmethod
    def invalid_data_type_error(data_type: str) -> str:
        return ('Invalid data. Expected a dictionary (object), '
                f'but got {data_type}.')


class APIV1ModerationEventErrorMessages:
    EVENT_NOT_FOUND = 'Moderation event not found.'
    EVENT_NOT_PENDING = 'The moderation event should be in PENDING status.'
    INVALID_UUID_FORMAT = 'Invalid UUID format.'
    PERMISSION_DENIED = 'You do not have permission to perform this action.'


# If the error isn’t field-specific, the non_field_errors key will be used
# for issues spanning multiple fields or related to the overall data
# object.
NON_FIELD_ERRORS_KEY = 'non_field_errors'


class APIV1LocationContributionKeys:
    LNG = 'lng'
    LAT = 'lat'


class APIV1MatchTypes:
    NEW_PRODUCTION_LOCATION = 'moderation_event_new_production_location'
    CONFIRMED_MATCH = 'moderation_event_confirmed_match'


LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX = (
    '[API V1 Location Contribution Approval]'
)

SINGLE_PAID_DOWNLOAD_RECORDS = 5000
