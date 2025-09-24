class ProductionLocationsResponseMapping:
    '''
    This class defines the fields that should be included in the API response for
    production locations. The fields correspond to the data stored in OpenSearch
    under the production-locations index. PRODUCTION_LOCATIONS contains the base
    fields returned for all endpoints, while PRODUCTION_LOCATION_BY_OS_ID adds
    additional fields for single location lookups.
    '''
    PRODUCTION_LOCATIONS = [
        "os_id",
        "name",
        "local_name",
        "description",
        "address",
        "geocoded_location_type",
        "geocoded_address",
        "business_url",
        "sector",
        "parent_company",
        "product_type",
        "location_type",
        "processing_type",
        "number_of_workers.min",
        "number_of_workers.max",
        "coordinates",
        "minimum_order_quantity",
        "average_lead_time",
        "percent_female_workers",
        "affiliations",
        "certifications_standards_regulations",
        "country.name",
        "country.alpha_2",
        "country.alpha_3",
        "country.numeric",
        "claim_status",
        "claimed_at",
        "historical_os_id",
        "rba_id",
        "duns_id",
        "lei_id",
    ]
    PRODUCTION_LOCATION_BY_OS_ID = PRODUCTION_LOCATIONS + [
        "opened_at",
        "closed_at",
        "estimated_annual_throughput",
        "actual_annual_energy_consumption",
    ]
