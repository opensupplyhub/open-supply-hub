from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class DateRangeValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []

        date_gte = data.get('date_gte')
        date_lt = data.get('date_lt')

        both_dates_error_message = (
            "Both 'date_gte' and 'date_lt' "
            "must be provided if one is present."
        )
        if (date_gte is not None and date_lt is None):
            errors.append({
                "field": "date_lt",
                "message": both_dates_error_message
            })
        elif (date_gte is None and date_lt is not None):
            errors.append({
                "field": "date_gte",
                "message": both_dates_error_message
            })

        if date_gte and date_lt and date_gte > date_lt:
            errors.append({
                "field": "date_gte",
                "message": (
                    "The 'date_gte' must be "
                    "less than or equal to 'date_lt'."
                )
            })

        return errors
