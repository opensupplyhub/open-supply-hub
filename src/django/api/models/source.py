import uuid
from django.db import models


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
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the source.'
    )
    # contributor_uuid = models.ForeignKey(
    #     'Contributor',
    #     to_field='uuid',
    #     db_column='contributor_uuid',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     editable=False,
    #     related_name='sources',
    #     help_text=(
    #         'The UUID of the contributor who submitted the facility data.'
    #     ),
    # )

    @property
    def display_name(self):
        name = self.contributor.name \
            if self.contributor else '[Unknown Contributor]'
        if self.facility_list:
            return f'{name} ({self.facility_list.name})'
        return name

    def __str__(self):
        return f'{self.display_name} ({self.id})'
