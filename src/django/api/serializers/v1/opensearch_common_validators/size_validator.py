from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class SizeValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data) -> list[dict]:
        errors: list[dict] = []
        size = data.get('size')
        size_limit = 250

        if size is None:
            return errors

        try:
            size = int(size)
            if size <= 0 or size > size_limit:
                errors.append({
                    "field": "size",
                    "message": (
                        f"Size must be a positive integer less than or equal "
                        f"to {size_limit}."
                    )
                })
        except ValueError:
            errors.append({
                "field": "size",
                "message": "Size must be a valid integer."
            })

        return errors
