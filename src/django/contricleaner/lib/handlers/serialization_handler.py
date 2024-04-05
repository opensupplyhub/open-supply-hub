from contricleaner.lib.dto.list_dto import ListDTO
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.handlers.list_row_handler import ListRowHandler
from contricleaner.lib.serializers.row_serializers.composite_row_serializer \
    import RowSerializer
from contricleaner.lib.serializers.row_serializers.composite_row_serializer \
    import CompositeRowSerializer
from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface
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
    .row_required_fields_serializer \
    import RowRequiredFieldsSerializer


class SerializationHandler(ListRowHandler):

    def handle(self, rows: list[dict]) -> ListDTO:
        composite_row_serializer = self.__construct_serializers()

        for row in rows:
            result = composite_row_serializer.validate(rows)
            if len(result['errors']) > 0:
                row =  RowDTO(
                raw_json=raw_row,
                name=dict_res.get("name", ""),
                clean_name=dict_res.get("clean_name", ""),
                address=dict_res.get("address", ""),
                clean_address=dict_res.get("clean_address", ""),
                country_code=dict_res.get("country_code", ""),
                sector=dict_res.get("sector", []),
                fields=dict_res.get("fields", {}),
                errors=dict_res.get("errors", []),
            )
        return ListDTO(rows=serialized_rows)

    def __construct_serializers(self) -> RowSerializer:
        split_pattern = r', |,|\|'

        composite_row_serializer = CompositeRowSerializer()
        leaf_serializers = (
            RowCleanFieldSerializer("name", "clean_name"),
            RowCleanFieldSerializer("address", "clean_address"),
            RowSectorSerializer(sector_cache, split_pattern),
            RowCountrySerializer(),
            RowRequiredFieldsSerializer(),
            RowFacilityTypeSerializer(split_pattern),
            RowEmptySerializer(),
        )

        for serializer in leaf_serializers:
            composite_row_serializer.add_validator(serializer)

        return composite_row_serializer
