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
            .__replace_invalid_data(row)
        return ContriCleanerSerializerCsv.__cleanup_data_csv(replaced_value)

    # TODO refactor xls cleanup according to OSDEV-660
    @staticmethod
    def __cleanup_data_csv(value: str) -> str:
        # Replace multiple commas with a single comma
        result_value = re.sub(r',\s*,*', ',', value)
        # Remove trailing comma
        result_value = result_value.rstrip(',')
        # Remove leading and trailing spaces
        return result_value.strip()
