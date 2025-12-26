from django.db.models import (
    Model,
    URLField,
    DateTimeField,
    CharField,
    TextChoices
)
from django.core.cache import cache


class WageIndicatorCountryData(Model):
    '''
    Stores WageIndicator data for countries including living wage
    and minimum wage information links.

    This is a reference data table optimized for fast lookups by country code.
    '''

    class LinkType(TextChoices):
        '''
        Link field types for WageIndicator data.
        NOTE: This is used by WageIndicatorLinkTextConfig model for choices.
        If you add/remove/rename URL fields in WageIndicatorCountryData model,
        update this class accordingly.
        '''
        LIVING_WAGE_NATIONAL = (
            'living_wage_link_national',
            'Living Wage Link National'
        )
        MINIMUM_WAGE_ENGLISH = (
            'minimum_wage_link_english',
            'Minimum Wage Link English'
        )
        MINIMUM_WAGE_NATIONAL = (
            'minimum_wage_link_national',
            'Minimum Wage Link National'
        )

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
        verbose_name = 'WageIndicator country'
        verbose_name_plural = 'WageIndicator countries'

    def __str__(self):
        return f'WageIndicator country data for {self.country_code}'

    def get_links_with_text(self):
        '''
        Returns all wage indicator links with their configured display text.
        '''
        # Cache the link texts since they rarely change.
        link_texts = cache.get('wage_indicator_link_texts')
        if link_texts is None:
            from api.models.wage_indicator_link_text_config import (
                WageIndicatorLinkTextConfig
            )
            link_texts = {
                link_text.link_type: link_text.display_text
                for link_text in WageIndicatorLinkTextConfig.objects.all()
            }
            # Cache for 1 hour.
            cache.set('wage_indicator_link_texts', link_texts, 3600)

        links = []
        for field in self._meta.get_fields():
            if isinstance(field, URLField):
                url = getattr(self, field.name)
                if url:  # Only include non-empty URLs.
                    links.append({
                        'url': url,
                        'text': link_texts.get(
                            field.name,
                            field.name.replace('_', ' ').title()  # Fallback.
                        ),
                        'type': field.name
                    })

        return links

    @classmethod
    def get_links_for_country(cls, country_code):
        '''
        Convenience method to get links with text for a specific country.
        '''
        try:
            data = cls.objects.get(country_code=country_code)
            return data.get_links_with_text()
        except cls.DoesNotExist:
            return []
