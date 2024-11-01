from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class StatusValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []
        status = data.get('status')

        if not status:
            return errors

        status_types = {'PENDING', 'RESOLVED'}

        if status not in status_types:
            errors.append({
                "field": "status",
                "message": f"'{status}' is not a valid status. \
                    Allowed values are 'PENDING' or 'RESOLVED'."
            })

        return errors
