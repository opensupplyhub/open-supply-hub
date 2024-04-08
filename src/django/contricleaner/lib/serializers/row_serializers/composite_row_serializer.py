import re
from typing import List, Dict

from contricleaner.lib.serializers.row_serializers.row_serializer \
    import RowSerializer


class CompositeRowSerializer(RowSerializer):
    __serializers: List[RowSerializer] = []

    def add_serializer(self, serializer: RowSerializer):
        self.__serializers.append(serializer)

    @staticmethod
    def clean_row(row: str) -> str:
        return CompositeRowSerializer.__clean_and_replace_data(row)

    @staticmethod
    def __clean_and_replace_data(data: Dict[str, str]) -> Dict[str, str]:
        invalid_keywords = ['N/A', 'n/a']
        dup_pattern = ',' + '{2,}'
        result_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove invalid keywords.
                for keyword in invalid_keywords:
                    value = value.replace(keyword, '')
                # Remove duplicates commas if exist.
                value = re.sub(dup_pattern, ',', value)
                # Remove comma in the end of the string if exist.
                value = value.rstrip(',')
                # Remove extra spaces if exist.
                value = value.strip()
            result_data[key] = value
        return result_data

    def validate(self, row: Dict) -> Dict:
        standard_fields = {
            "name",
            "clean_name",
            "address",
            "clean_address",
            "country_code",
            "sector",
            "errors"
        }

        res = {
            "errors": [],
        }

        copied_row = row.copy()
        cleaned_row = CompositeRowSerializer.clean_row(copied_row)

        for validator in self.validators:
            res = validator.validate(cleaned_row, res)

        dict_res = {
            "fields": {},
        }

        for res_key, res_value in res.items():
            if res_key in standard_fields:
                dict_res[res_key] = res_value
            else:
                dict_res["fields"][res_key] = res_value

        return dict_res
