from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class StatusValidator(OpenSearchValidationInterface):
    VALID_STATUSES = {'PENDING', 'APPROVED', 'REJECTED'}

    def validate_opensearch_params(self, data):
        errors = []
        status = data.get('status')

        if not status:
            return errors

        if not isinstance(status, list):
            errors.append({
                "field": "status",
                "message": "Status must be a list of values."
            })
        elif not all(item in self.VALID_STATUSES for item in status):
            invalid_statuses = [item for item in status if
                                item not in self.VALID_STATUSES]
            errors.append({
                "field": "status",
                "message": (
                    f"Invalid source(s) {invalid_statuses}. "
                    "Allowed values are 'PENDING','APPROVED' or 'REJECTED'."
                )
            })

        return errors
