from rest_framework import serializers


class OrganizationContributionsQueryParamsSerializer(serializers.Serializer):
    LISTS = 'lists'
    CONTRIBUTIONS = 'contributions'
    CLAIMS = 'claims'

    type = serializers.ChoiceField(
        choices=(LISTS, CONTRIBUTIONS, CLAIMS),
        required=False,
        default=LISTS,
    )
    member = serializers.IntegerField(required=False, min_value=1)


class OrganizationDashboardQueryParamsSerializer(serializers.Serializer):
    """
    Filters shared by the dashboard summary and facilities endpoints.
    `member` is a contributor id; dates bound the submission date.
    """
    member = serializers.IntegerField(required=False, min_value=1)
    country = serializers.CharField(required=False, max_length=2)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    claimed = serializers.BooleanField(required=False, allow_null=True,
                                       default=None)

    def validate_country(self, value):
        return value.upper()

    def validate(self, data):
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                {'date_to': ['date_to must not be before date_from.']}
            )
        return data
