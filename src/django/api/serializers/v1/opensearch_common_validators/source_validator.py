from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class SourceValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []
        source = data.get('source')

        if not source:
            return errors

        valid_sources = {'SLC', 'API'}

        if source not in valid_sources:
            errors.append({
                "field": "source",
                "message": f"'{source}' is not a valid source. \
                    Allowed values are 'SLC' or 'API'."
            })

        return errors
