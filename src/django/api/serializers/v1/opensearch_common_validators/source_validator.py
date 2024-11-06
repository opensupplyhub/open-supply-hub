from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class SourceValidator(OpenSearchValidationInterface):
    VALID_SOURCES = {'SLC', 'API'}

    def validate_opensearch_params(self, data):
        errors = []
        source = data.get('source')

        if not source:
            return errors

        if not isinstance(source, list):
            errors.append({
                "field": "source",
                "message": "Source must be a list of values."
            })
        elif not all(item in self.VALID_SOURCES for item in source):
            invalid_sources = [item for item in source if \
                               item not in self.VALID_SOURCES]
            errors.append({
                "field": "source",
                "message": (
                    f"Invalid source(s) {invalid_sources}. "
                    "Allowed values are 'SLC' or 'API'."
                )
            })

        return errors
