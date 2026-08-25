from django.db import models


class FacilityProcessingValue(models.Model):
    """Searchable facility and processing value maintained by SQL triggers."""

    pk = models.CompositePrimaryKey('kind', 'identity')
    kind = models.TextField()
    identity = models.TextField()
    value = models.TextField()
    facility_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'api_facility_processing_value'
