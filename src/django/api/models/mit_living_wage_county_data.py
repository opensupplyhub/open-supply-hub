from django.db.models import Model, DateTimeField, CharField


class MITLivingWageCountyData(Model):
    '''
    Stores MIT Living Wage data of county by geo id.
    '''

    us_geoid_county = CharField(
        max_length=50,
        help_text='The Geo Id of county (US)'
    )
    country_code = CharField(
        max_length=2,
        help_text='ISO 3166-1 alpha-2 country code (e.g., US, MX, PR).'
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'MIT Living Wage County Data'
        verbose_name_plural = 'MIT Living Wage County Data'

    def __str__(self):
        return f'MIT Living Wage county data for {self.country_code}'
