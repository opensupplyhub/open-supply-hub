from django.utils import timezone
from ...mail import send_report_result


def update_facility_activity_report_status(
    facility_activity_report,
    request,
    status
):
    status_change_reason = request.data.get('status_change_reason')
    now = str(timezone.now())

    facility_activity_report.status_change_reason = status_change_reason
    facility_activity_report.status_change_by = request.user
    facility_activity_report.status_change_date = now
    facility_activity_report.status = status
    if status == 'CONFIRMED':
        facility_activity_report.approved_at = now
    facility_activity_report.save()

    send_report_result(facility_activity_report)

    return facility_activity_report
