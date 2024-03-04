from .row_serializer import RowSerializer


class SectorCacheInterface:
    @property
    def sector_map(self) -> dict:
        pass


class RowSectorSerializer(RowSerializer):
    def __init__(self, cache=SectorCacheInterface):
        self.cache = cache
        self.sectors = []
        self.product_types = []

    def validate(self, row: dict, current: dict) -> dict:

    # # facility_type_processing_type is a special "meta" field that attempts to
        # # simplify the submission process for contributors.
        # if (raw_data.get('facility_type_processing_type')):
        #     if raw_data.get('facility_type') is None:
        #         raw_data['facility_type'] = \
        #             raw_data['facility_type_processing_type']
        #     if raw_data.get('processing_type') is None:
        #         raw_data['processing_type'] = \
        #             raw_data['facility_type_processing_type']
        # # Add a facility_type extended field if the user only
        # # submitted a processing_type
        # elif (raw_data.get('processing_type') and
        #       raw_data.get('facility_type') is None):
        #     raw_data['facility_type'] = raw_data['processing_type']
        # # Add a processing_type extended field if the user only
        # # submitted a facility_type
        # elif (raw_data.get('facility_type') and
        #       raw_data.get('processing_type') is None):
        #     raw_data['processing_type'] = raw_data['facility_type']



        # self.parse_all_values(
        #     set([
        #         *row.get('sector', []),
        #         *row.get('product_type', []),
        #         *row.get('sector_product_type', [])
        #     ])
        # )


        # if isinstance(row.get('sector', str)):
        #     current["sector"]=row["sector"].split(",")
        # else:
        #     current["sector"]=[]

        # "asdfasdf,asdfasdf,asdf,asd,asdf"=>["asdfasdf", "asdfasdf", "asdf", "asd", "asdf"]
        # ["asdfasdf,asdfasdf,asdf,asd,asdf", "asdfasdf,asdfasdf,asdf,asd,asdf"] =>["asdfasdf", "asdfasdf", "asdf", "asd", "asdf", "asdfasdf", "asdfasdf", "asdf", "asd", "asdf" ]

        current["sector"] = row["sector"].split(",")
        print('current', current)
        return current

    # def parse_all_values(self, all_values):
    #     DEFAULT_SECTOR_NAME = 'Unspecified'

    #     sector_map = SectorCacheInterface.sector_map

    #     for value in all_values:
    #         clean_value = self.clean_value(value)
    #         if (clean_value in sector_map):
    #             self.sectors.append(sector_map[clean_value])
    #         else:
    #             self.product_types.append(value)

    #         if len(self.sectors) == 0:
    #             self.sectors.append(DEFAULT_SECTOR_NAME)

    # def sort_values(self):
    #     self.sectors.sort()
    #     self.product_types.sort()

    # def clean_value(self, value):
    #     return value.lower().strip()
