from django.db import models


class EmbedField(models.Model):
    """
    Data fields to include on facilities in an embedded map
    """
    class Meta:
        unique_together = ('embed_config', 'order')

    embed_config = models.ForeignKey(
        'EmbedConfig',
        null=False,
        on_delete=models.CASCADE,
        help_text='The embedded map configuration which uses this field'
    )
    column_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The column name of the field.')
    display_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The name to display for the field.')
    visible = models.BooleanField(
        default=False,
        help_text='Whether or not to display this field.'
    )
    order = models.IntegerField(
        null=False,
        blank=False,
        help_text='The sort order of the field.')
    searchable = models.BooleanField(
        default=False,
        help_text='Whether or not to include this field in search.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            'Column Name {column_name} - Order: {order} ').format(
            **self.__dict__)
