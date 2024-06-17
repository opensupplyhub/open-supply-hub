from rest_framework.serializers import (
    Serializer,
    ValidationError,
    BooleanField,
    DateField,
    ListField,
    IntegerField
)


class MergeQueryParamsSerializer(Serializer):
    detail = BooleanField(default=False, required=False)
    date_greater_than_or_equal = DateField(default='', required=False)
    date_less_than = DateField(default='', required=False)
    contributors = ListField(
        default=[],
        child=IntegerField(min_value=0),
        allow_empty=False,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request:
            allowed_params = set(field for field in self.fields.keys())
            unexpected_params = set(
                request.query_params.keys()
            ) - allowed_params

            if unexpected_params:
                errorTxt = "Unexpected query parameters: {}"

                raise ValidationError(
                    errorTxt.format(', '.join(unexpected_params))
                )

    def validate(self, data):
        self._check_start_and_before(data)

        return data

    def _check_start_and_before(self, data):
        """
        Check that start date is before end date.
        """
        date_gte = data.get('date_greater_than_or_equal')
        date_lt = data.get('date_less_than')

        if date_gte and date_lt \
           and (date_gte > date_lt or date_gte == date_lt):
            raise ValidationError(
                "date_greater_than_or_equal must be less than date_less_than")
