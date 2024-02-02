from django.db import models


class ArrayLength(models.Func):
    """
    A Func subclass that can be used in a QuerySet.annotate() call to invoke
    the Postgres cardinality function on an array field, which returns the
    length of the array.
    """
    function = 'CARDINALITY'


class Source(models.Model):
    LIST = 'LIST'
    SINGLE = 'SINGLE'

    SOURCE_TYPE_CHOICES = (
        (LIST, LIST),
        (SINGLE, SINGLE),
    )

    contributor = models.ForeignKey(
        'Contributor',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The contributor who submitted the facility data'
    )
    source_type = models.CharField(
        null=False,
        max_length=6,
        choices=SOURCE_TYPE_CHOICES,
        help_text='Did the the facility data arrive in a list or a single item'
    )
    facility_list = models.OneToOneField(
        'FacilityList',
        null=True,
        on_delete=models.PROTECT,
        help_text='The related list if the type of the source is LIST.'
    )
    is_active = models.BooleanField(
        null=False,
        default=True,
        help_text=('True if items from the source should be shown as being '
                   'associated with the contributor')
    )
    is_public = models.BooleanField(
        null=False,
        default=True,
        help_text=('True if the public can see factories from this list '
                   'are associated with the contributor.')
    )
    create = models.BooleanField(
        null=False,
        default=True,
        help_text=('Should a facility or facility match be created from the '
                   'facility data')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self.__original_is_active = self.is_active

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(Source, self).save(force_insert, force_update, *args, **kwargs)

        if self.__original_is_active and not self.is_active:
            from .ppemixin import PPEMixin
            from .facility.facility_match import FacilityMatch

            for item in self.facilitylistitem_set.annotate(
                ppe_product_types_len=ArrayLength('ppe_product_types')
            ).filter(PPEMixin.PPE_FILTER):
                for match in (item.facilitymatch_set
                              .filter(is_active=True)
                              .exclude(status=FacilityMatch.REJECTED)
                              .exclude(status=FacilityMatch.PENDING)):
                    if match.facility.revert_ppe(item):
                        match.facility.save()
        self.__original_is_active = self.is_active

    @property
    def display_name(self):
        name = self.contributor.name \
            if self.contributor else '[Unknown Contributor]'
        if self.facility_list:
            return f'{name} ({self.facility_list.name})'
        return name

    def __str__(self):
        return f'{self.display_name} ({self.id})'
