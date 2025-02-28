import logging
import re
from typing import List, Dict

from contricleaner.lib.serializers.row_serializers.row_serializer \
    import RowSerializer

logger = logging.getLogger(__name__)

class CompositeRowSerializer(RowSerializer):

    def __init__(self) -> None:
        self.__serializers: List[RowSerializer] = []

    def add_serializer(self, serializer: RowSerializer):
        self.__serializers.append(serializer)

    @staticmethod
    def clean_row(row: str) -> str:
        return CompositeRowSerializer.__clean_and_replace_data(row)

    @staticmethod
    def __add_space_after_comma(value: str) -> str:
        return re.sub(r',', ', ', value)

    @staticmethod
    def __clean_commas(value: str) -> str:
        # Remove spaces after and before commas
        cleaned_value = re.sub(r'\s*,\s*', ',', value)
        # Remove duplicates commas
        cleaned_value = re.sub(r',+', ',', cleaned_value)
        # Remove leading and trailing commas
        cleaned_value = cleaned_value.strip(',')
        return cleaned_value

    @staticmethod
    def __remove_double_quotes(value: str) -> str:
        quotes_to_remove = ['"', '“', '”', '‟', '„', '«', '»', '‹', '›']
        for symbol in quotes_to_remove:
            value = value.replace(symbol, '')
        logger.info(f'$$$$$ value after ContriCleaner: {value}')
        return value

    @staticmethod
    def __remove_duplicate_spaces(value: str):
        return re.sub(' +', ' ', value)

    @staticmethod
    def __clean_and_replace_data(data: Dict[str, str]) -> Dict[str, str]:
        invalid_keywords = ['N/A', 'n/a']
        result_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove invalid keywords.
                for keyword in invalid_keywords:
                    value = value.replace(keyword, '')
                value = CompositeRowSerializer.__clean_commas(value)
                value = CompositeRowSerializer.__add_space_after_comma(value)
                value = CompositeRowSerializer.__remove_double_quotes(value)
                value = CompositeRowSerializer.__remove_duplicate_spaces(value)
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

        for serializer in self.__serializers:
            res = serializer.validate(cleaned_row, res)

        dict_res = {
            "fields": {},
        }

        for res_key, res_value in res.items():
            if res_key in standard_fields:
                dict_res[res_key] = res_value
            else:
                dict_res["fields"][res_key] = res_value

        return dict_res
