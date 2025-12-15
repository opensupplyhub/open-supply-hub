from django.db.models import Model, URLField, DateTimeField, CharField


class WageIndicatorCountryData(Model):
    '''
    Stores WageIndicator data for countries including living wage
    and minimum wage information links.

    This is a reference data table optimized for fast lookups by country code.
    '''

    # System partner field constant.
    PARTNER_FIELD_NAME = 'wage_indicator'

    country_code = CharField(
        max_length=2,
        primary_key=True,
        help_text='ISO 3166-1 alpha-2 country code (e.g., US, GB, CN).'
    )
    living_wage_link_national = URLField(
        max_length=500,
        help_text='Living wage benchmark link in national language.'
    )
    minimum_wage_link_english = URLField(
        max_length=500,
        help_text='Minimum wage information link in English.'
    )
    minimum_wage_link_national = URLField(
        max_length=500,
        help_text='Minimum wage information link in national language.'
    )

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Wage Indicator Country Data'
        verbose_name_plural = 'Wage Indicator Country Data'

    def __str__(self):
        return f'Wage indicator country data for {self.country_code}'
