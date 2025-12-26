from django.db.models import Model, CharField, DateTimeField

from api.models.wage_indicator_country_data import WageIndicatorCountryData


class WageIndicatorLinkTextConfig(Model):
    '''
    Stores configurable display text for different WageIndicator link types.
    Link types are automatically derived from LinkType enum in the
    WageIndicatorCountryData model.

    This allows admins to customize the text displayed for each type of wage
    indicator link without storing redundant data for every country.
    '''

    link_type = CharField(
        max_length=50,
        primary_key=True,
        choices=WageIndicatorCountryData.LinkType.choices,
        help_text=('Type of wage indicator link. The choices are field names '
                   'in the WageIndicatorCountryData model. This field is a '
                   'connector to relevant URL field in the '
                   'WageIndicatorCountryData model.')
    )
    display_text = CharField(
        max_length=200,
        help_text=('Display text to show for this link type. This is the '
                   'text that will be shown to the user when they click on '
                   'the wage indicator link of the relevant type like living '
                   'wage link national, minimum wage link English, etc.')
    )

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'WageIndicator link label'
        verbose_name_plural = 'WageIndicator link labels'

    def __str__(self):
        return ("The wage indicator link "
                f"'{self.link_type.replace('_', ' ').title()}' "
                f"has the link display text: '{self.display_text}'. This data "
                "then maps to the WageIndicatorCountryData model's "
                f"'{self.link_type.replace('_', ' ').title()}' field which is "
                "a URL field.")
