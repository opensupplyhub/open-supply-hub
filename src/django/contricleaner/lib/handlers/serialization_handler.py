from typing import List, Dict

from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.handlers.list_row_handler import ListRowHandler
from contricleaner.lib.serializers.row_serializers.\
    row_additional_ids_serializer import RowAdditionalIdsSerializer
from contricleaner.lib.serializers.row_serializers.\
    row_parent_company_os_id_serializer import RowParentCompanyOSIDSerializer
from contricleaner.lib.serializers.row_serializers.composite_row_serializer \
    import RowSerializer
from contricleaner.lib.serializers.row_serializers.composite_row_serializer \
    import CompositeRowSerializer
from contricleaner.lib.client_abstractions.cache_interface import (
    CacheInterface
)
from contricleaner.lib.client_abstractions.lookup_interface import (
    LookupInterface
)
from contricleaner.lib.serializers.row_serializers.row_clean_field_serializer \
    import RowCleanFieldSerializer
from contricleaner.lib.serializers.row_serializers.row_country_serializer \
    import RowCountrySerializer
from contricleaner.lib.serializers.row_serializers.row_empty_serializer \
    import RowEmptySerializer
from contricleaner.lib.serializers.row_serializers.\
    row_facility_type_serializer import RowFacilityTypeSerializer
from contricleaner.lib.serializers.row_serializers.row_sector_serializer \
    import RowSectorSerializer
from contricleaner.lib.serializers.row_serializers \
    .row_required_fields_serializer import RowRequiredFieldsSerializer
from contricleaner.lib.serializers.row_serializers.row_coordinates_serializer \
    import RowCoordinatesSerializer


class SerializationHandler(ListRowHandler):

    def __init__(
            self,
            sector_cache: CacheInterface,
            os_id_lookup: LookupInterface
    ) -> None:
        self.__sector_cache = sector_cache
        self.__os_id_lookup = os_id_lookup

    def handle(self, rows: List[Dict]) -> ListDTO:
        serialized_rows = []
        composite_row_serializer = self.__construct_serializers()

        for row in rows:
            serialized_row_dict = composite_row_serializer.validate(row)
            serialized_row = RowDTO(
                raw_json=row,
                name=serialized_row_dict.get('name', ''),
                clean_name=serialized_row_dict.get('clean_name', ''),
                address=serialized_row_dict.get('address', ''),
                clean_address=serialized_row_dict.get('clean_address', ''),
                country_code=serialized_row_dict.get('country_code', ''),
                sector=serialized_row_dict.get('sector', []),
                fields=serialized_row_dict.get('fields', {}),
                errors=serialized_row_dict.get('errors', []),
            )
            serialized_rows.append(serialized_row)

        return ListDTO(rows=serialized_rows)

    def __construct_serializers(self) -> RowSerializer:
        split_pattern = r', |,|\|'

        composite_row_serializer = CompositeRowSerializer()
        leaf_serializers = (
            RowCleanFieldSerializer('name', 'clean_name'),
            RowCleanFieldSerializer('address', 'clean_address'),
            RowSectorSerializer(self.__sector_cache, split_pattern),
            RowCountrySerializer(),
            RowRequiredFieldsSerializer(),
            RowFacilityTypeSerializer(split_pattern),
            RowCoordinatesSerializer(),
            RowAdditionalIdsSerializer(),
            RowParentCompanyOSIDSerializer(
                self.__os_id_lookup,
                split_pattern
            ),
            RowEmptySerializer(),
        )

        for serializer in leaf_serializers:
            composite_row_serializer.add_serializer(serializer)

        return composite_row_serializer
