from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone

from api.constants import OrganizationSettings
from api.models.api.api_limit import ApiLimit
from api.models.download_log import DownloadLog
from api.models.facility_download_limit import FacilityDownloadLimit
from api.models.request_log import RequestLog
from api.serializers.user_api_info_serializer import UserApiInfoSerializer


class OrganizationUsageService:
    """
    How much the organization's current members download and call the
    API, for the dashboard.

    Usage belongs to each member's own account, with its own download
    allowance and API limit; nothing here is pooled or recorded against
    the organization. The figures therefore cover the people who are
    members now, including what they did before joining, and leave out
    former members.
    """

    def __init__(self, organization):
        self.organization = organization

    def usage(self):
        period_days = OrganizationSettings.USAGE_PERIOD_DAYS
        now = timezone.now()
        since = now - timedelta(days=period_days)
        start_of_year = now.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )

        memberships = list(
            self.organization.active_memberships()
            .select_related('user__contributor')
            .order_by('joined_at')
        )
        user_ids = [membership.user_id for membership in memberships]

        downloads = {
            row['user_id']: row
            for row in DownloadLog.objects
            .filter(user_id__in=user_ids, created_at__gte=start_of_year)
            .values('user_id')
            .annotate(
                recent_count=Count('id', filter=Q(created_at__gte=since)),
                recent_records=Sum(
                    'record_count', filter=Q(created_at__gte=since)
                ),
                year_records=Sum('record_count'),
            )
        }
        allowances = {
            limit.user_id: limit
            for limit in FacilityDownloadLimit.objects.filter(
                user_id__in=user_ids
            )
        }
        api_calls = {
            row['user_id']: row['calls']
            for row in RequestLog.objects
            .filter(user_id__in=user_ids, created_at__gte=since)
            .values('user_id')
            .annotate(calls=Count('id'))
        }
        api_user_ids = set(
            self.organization.active_memberships()
            .filter(user__groups__isnull=False)
            .values_list('user_id', flat=True)
        )

        members = [
            self._member_usage(
                membership,
                downloads.get(membership.user_id, {}),
                allowances.get(membership.user_id),
                api_calls.get(membership.user_id, 0),
                membership.user_id in api_user_ids,
            )
            for membership in memberships
        ]

        return {
            'period_days': period_days,
            'members': members,
            'totals': {
                'downloads': sum(
                    member['downloads']['count'] for member in members
                ),
                'downloaded_records': sum(
                    member['downloads']['records'] for member in members
                ),
                'api_calls': sum(
                    member['api']['calls'] for member in members
                    if member['api'] is not None
                ),
            },
        }

    @staticmethod
    def _member_usage(membership, downloads, allowance, api_calls,
                      has_api_access):
        user = membership.user
        contributor = getattr(user, 'contributor', None)

        api = None
        if has_api_access and contributor is not None:
            api = {
                'calls': api_calls,
                **OrganizationUsageService._api_period(user, contributor),
            }

        return {
            'membership_uuid': membership.uuid,
            'email': user.email,
            'contributor_name': contributor.name if contributor else None,
            'downloads': {
                'count': downloads.get('recent_count') or 0,
                'records': downloads.get('recent_records') or 0,
                'records_this_year': downloads.get('year_records') or 0,
                # None until the member's first download creates their
                # allowance.
                'free_records_left': (
                    allowance.free_download_records if allowance else None
                ),
                'paid_records_left': (
                    allowance.paid_download_records if allowance else None
                ),
            },
            'api': api,
        }

    @staticmethod
    def _api_period(user, contributor):
        """
        The member's API limit and what they used of it in its current
        period, counted the way their own API settings page counts it.
        Both are None when no limit is set for their contributor.
        """
        limit = ApiLimit.objects.filter(contributor=contributor).first()
        if limit is None:
            return {
                'limit': None,
                'renewal_period': None,
                'calls_this_period': None,
            }

        info = UserApiInfoSerializer(user.id, contributor.id).data
        return {
            'limit': limit.period_limit,
            'renewal_period': limit.renewal_period or None,
            'calls_this_period': (
                info['current_usage'] if limit.renewal_period else None
            ),
        }
