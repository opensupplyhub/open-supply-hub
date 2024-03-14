import re
from contricleaner.lib.serializers.contri_cleaner_serializer \
    import ContriCleanerSerializer


class ContriCleanerSerializerCsv(ContriCleanerSerializer):
    def __init__(self, row_serializer, INVALID_KEYWORDS):
        super().__init__(row_serializer, INVALID_KEYWORDS)

    @staticmethod
    def _clean_row(row: str) -> str:
        replaced_value = super(ContriCleanerSerializerCsv,
                               ContriCleanerSerializerCsv)\
            ._replace_invalid_data(row)
        return ContriCleanerSerializerCsv.__cleanup_data_csv(replaced_value)

    # TODO refactor xls cleanup according to OSDEV-660
    @staticmethod
    def __cleanup_data_csv(value: str) -> str:
        dup_pattern = ',' + '{2,}'
        # Remove duplicates commas if exist.
        result_value = re.sub(dup_pattern, ',', value)
        # Remove comma in the end of the string if exist.
        result_value = result_value.rstrip(',')
        # Remove extra spaces if exist.
        return result_value.strip()
