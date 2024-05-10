from django.db import models


class NonstandardField(models.Model):
    """
    Nonstandard data fields available to include on facilities in an
    embedded map
    """
    class Meta:
        unique_together = ('contributor', 'column_name')

    # Keys in this set must be kept in sync with
    # defaultNonstandardFieldLabels in /src/react/src/util/embeddedMap.js
    EXTENDED_FIELDS = {
        'parent_company': 'Parent Company',
        'product_type': 'Product Type',
        'number_of_workers': 'Number of Workers',
        'facility_type': 'Facility Type',
        'processing_type': 'Processing Type',
    }

    contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.CASCADE,
        help_text='The contributor who submitted this field'
    )
    column_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The column name of the field.')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            'Contributor ID: {contributor_id} - ' +
            'Column Name: {column_name}'
        ).format(**self.__dict__)
