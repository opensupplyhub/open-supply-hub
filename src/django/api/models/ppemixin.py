from django.contrib.postgres import fields as postgres
from django.db import models
from django.db.models import Q


class PPEMixin(models.Model):
    class Meta:
        abstract = True

    # TODO: #1038 Remove the isnull checks after the fields are made
    # non-null
    PPE_FILTER = (
        (Q(ppe_product_types__isnull=False)
         & Q(ppe_product_types_len__gt=0))
        |
        (Q(ppe_contact_phone__isnull=False)
         & ~Q(ppe_contact_phone=''))
        |
        (Q(ppe_contact_email__isnull=False)
         & ~Q(ppe_contact_email=''))
        |
        (Q(ppe_website__isnull=False)
         & ~Q(ppe_website=''))
    )

    ppe_product_types = postgres.ArrayField(
        models.CharField(
            null=False,
            blank=False,
            max_length=100,
            help_text=('A type of personal protective equipment produced at '
                       'the facility'),
            verbose_name='ppe product type',
        ),
        null=True,
        blank=True,
        help_text=('The types of personal protective equipment produced at '
                   'the facility'),
        verbose_name='ppe product types')
    ppe_contact_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='ppe contact email',
        help_text='The contact email for PPE-related discussion')
    ppe_contact_phone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='ppe contact phone',
        help_text='The contact phone number for PPE-related discussion')
    ppe_website = models.URLField(
        null=True,
        blank=True,
        verbose_name='ppe website',
        help_text='The website for PPE information')

    @property
    def has_ppe_product_types(self):
        return (self.ppe_product_types is not None
                and self.ppe_product_types != [])

    @property
    def has_ppe_contact_phone(self):
        return (self.ppe_contact_phone is not None
                and self.ppe_contact_phone != '')

    @property
    def has_ppe_contact_email(self):
        return (self.ppe_contact_email is not None
                and self.ppe_contact_email != '')

    @property
    def has_ppe_website(self):
        return (self.ppe_website is not None and self.ppe_website != '')
