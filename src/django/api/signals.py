from django.db.models.signals import post_delete
from django.dispatch import receiver
from api.models.facility.facility import Facility


@receiver(post_delete, sender=Facility)
def facility_post_delete(sender, **kwargs):
    print('Hi OpenSearch!')
