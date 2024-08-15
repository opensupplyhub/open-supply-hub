import re
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class CountryValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []
        countries = data.get('country')
        valid_country_value_regexp = r'^[A-Z]{2}$'

        if not countries:
            return errors

        if isinstance(countries, str):
            countries = [countries]

        for country in countries:
            if not re.match(valid_country_value_regexp, country):
                errors.append({
                    "field": "country",
                    "message":
                        f"'{country}' is not a valid alpha-2 country code."
                })

        return errors
