from django.db.migrations import Migration, RunPython

from api.models.source import Source
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch


def remove_sources_without_contributor_and_related_data(apps, schema_editor):
    """
    Remove records from the Source table where the contributor is null
    and remove all data related to these records
    """

    sources_without_contributor = Source.objects.filter(
        contributor=None
    ).order_by("-id")

    for source in sources_without_contributor:
        facility_list = FacilityList.objects.get(id=source.facility_list.id)
        facility_list_items = FacilityListItem.objects.filter(
            source_id=source.id
        )

        for facility_list_item in facility_list_items:
            FacilityMatch.objects.filter(
                facility_list_item_id=facility_list_item.id
            ).delete()
            facility = facility_list_item.facility

            if facility.created_from_id == facility_list_item.id:
                replacement_item = (
                    FacilityListItem.objects.filter(facility_id=facility.id)
                    .exclude(id=facility_list_item.id)
                    .last()
                )

                if replacement_item:
                    facility.created_from_id = replacement_item.id
                    facility.save()

            facility_list_item.delete()

        source.delete()
        facility_list.delete()


class Migration(Migration):
    dependencies = [
        ("api", "0133_introduce_tile_caching"),
    ]

    operations = [
        RunPython(
            remove_sources_without_contributor_and_related_data, RunPython.noop
        ),
    ]
