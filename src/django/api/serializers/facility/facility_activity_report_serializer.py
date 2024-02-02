from rest_framework.serializers import (
  ModelSerializer,
  SerializerMethodField,
)
from ...models import FacilityActivityReport


class FacilityActivityReportSerializer(ModelSerializer):
    reported_by_user = SerializerMethodField()
    reported_by_contributor = SerializerMethodField()
    facility_name = SerializerMethodField()
    status_change_by = SerializerMethodField()

    class Meta:
        model = FacilityActivityReport
        fields = ('facility', 'reported_by_user', 'reported_by_contributor',
                  'closure_state', 'approved_at', 'status_change_reason',
                  'status', 'status_change_reason', 'status_change_by',
                  'status_change_date', 'created_at', 'updated_at', 'id',
                  'reason_for_report', 'facility_name')

    def get_reported_by_user(self, instance):
        return instance.reported_by_user.email

    def get_reported_by_contributor(self, instance):
        return instance.reported_by_contributor.name

    def get_facility_name(self, instance):
        return instance.facility.name

    def get_status_change_by(self, instance):
        if instance.status_change_by is None:
            return None
        return instance.status_change_by.email
