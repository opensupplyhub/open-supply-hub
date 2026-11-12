from datetime import datetime, time

from django.db.models import (
    Count,
    Exists,
    F,
    Func,
    OuterRef,
    Q,
    Subquery,
)
from django.db.models.functions import TruncMonth
from django.utils import timezone

from api.constants import FacilityClaimStatuses, OrganizationSettings
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.moderation_event import ModerationEvent
from api.models.source import Source
from countries.lib.countries import COUNTRY_NAMES

# How many countries and sectors the summary breaks out before the rest
# would only add noise to a chart.
TOP_BREAKDOWN_ROWS = 15


def _approved_claims(facility_ref='facility_id'):
    return FacilityClaim.objects.filter(
        facility_id=OuterRef(facility_ref),
        status=FacilityClaimStatuses.APPROVED,
    )


def _start_of_day(day):
    return timezone.make_aware(datetime.combine(day, time.min))


def _end_of_day(day):
    return timezone.make_aware(datetime.combine(day, time.max))


class OrganizationDashboardService:
    """
    The paid organization dashboard: the production locations an
    organization's members submitted, with totals and claimed data.

    A submission is a list item or single contribution that resolved to
    a production location, recorded against the organization through
    its source. Sources that were replaced or deactivated do not count.
    Submissions by former members stay in, because the organization
    keeps what was contributed for it.
    """

    def __init__(self, organization, filters=None):
        self.organization = organization
        self.filters = filters or {}

    def submissions(self):
        queryset = FacilityListItem.objects.filter(
            source__organization=self.organization,
            source__is_active=True,
            status__in=FacilityListItem.COMPLETE_STATUSES,
            facility__isnull=False,
        )

        member = self.filters.get('member')
        if member:
            queryset = queryset.filter(source__contributor_id=member)

        country = self.filters.get('country')
        if country:
            queryset = queryset.filter(facility__country_code=country)

        date_from = self.filters.get('date_from')
        if date_from:
            queryset = queryset.filter(
                created_at__gte=_start_of_day(date_from)
            )

        date_to = self.filters.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=_end_of_day(date_to))

        claimed = self.filters.get('claimed')
        if claimed is not None:
            queryset = queryset.annotate(
                has_approved_claim=Exists(_approved_claims())
            ).filter(has_approved_claim=claimed)

        return queryset

    def facility_rows(self):
        """Submissions, newest first, ready for the facilities table."""
        return (
            self.submissions()
            .select_related(
                'facility',
                'source__contributor',
                'source__facility_list',
            )
            .annotate(
                claimed_at=Subquery(
                    _approved_claims()
                    .order_by('-status_change_date')
                    .values('status_change_date')[:1]
                ),
                is_claimed=Exists(_approved_claims()),
            )
            .order_by('-created_at', '-id')
        )

    @staticmethod
    def serialize_row(item):
        facility_list = item.source.facility_list
        contributor = item.source.contributor
        return {
            'submission_id': item.id,
            'os_id': item.facility_id,
            'name': item.facility.name,
            'address': item.facility.address,
            'country_code': item.facility.country_code,
            'country_name': COUNTRY_NAMES.get(
                item.facility.country_code, item.facility.country_code
            ),
            'submitted_at': item.created_at,
            'submitted_by': {
                'contributor_id': contributor.id,
                'contributor_name': contributor.name,
            } if contributor else None,
            'source_type': item.source.source_type,
            'list': {
                'id': facility_list.id,
                'name': facility_list.name,
            } if facility_list else None,
            'is_claimed': item.is_claimed,
            'claimed_at': item.claimed_at,
        }

    def summary(self):
        submissions = self.submissions()

        totals = submissions.aggregate(
            total_submissions=Count('id'),
            total_facilities=Count('facility_id', distinct=True),
        )
        total_facilities = totals['total_facilities']

        claimed_facilities = (
            submissions
            .filter(Exists(_approved_claims()))
            .aggregate(count=Count('facility_id', distinct=True))['count']
        )

        by_member = [
            {
                'contributor_id': row['source__contributor_id'],
                'contributor_name': row['source__contributor__name'],
                'facilities': row['facilities'],
                'submissions': row['submissions'],
            }
            for row in submissions
            .values('source__contributor_id', 'source__contributor__name')
            .annotate(
                facilities=Count('facility_id', distinct=True),
                submissions=Count('id'),
            )
            .order_by('-facilities', 'source__contributor__name')
        ]

        by_country = [
            {
                'country_code': row['facility__country_code'],
                'country_name': COUNTRY_NAMES.get(
                    row['facility__country_code'],
                    row['facility__country_code'],
                ),
                'facilities': row['facilities'],
            }
            for row in submissions
            .values('facility__country_code')
            .annotate(facilities=Count('facility_id', distinct=True))
            .order_by('-facilities', 'facility__country_code')
            [:TOP_BREAKDOWN_ROWS]
        ]

        by_month = [
            {
                'month': row['month'].strftime('%Y-%m'),
                'facilities': row['facilities'],
                'submissions': row['submissions'],
            }
            for row in submissions
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(
                facilities=Count('facility_id', distinct=True),
                submissions=Count('id'),
            )
            .order_by('month')
        ]

        by_source_type = {
            row['source__source_type']: {
                'facilities': row['facilities'],
                'submissions': row['submissions'],
            }
            for row in submissions
            .values('source__source_type')
            .annotate(
                facilities=Count('facility_id', distinct=True),
                submissions=Count('id'),
            )
        }

        return {
            'total_facilities': total_facilities,
            'total_submissions': totals['total_submissions'],
            'claimed_facilities': claimed_facilities,
            'unclaimed_facilities': total_facilities - claimed_facilities,
            'pending_moderation': self._pending_moderation_count(),
            'by_member': by_member,
            'by_country': by_country,
            'by_month': by_month,
            'by_sector': self._by_sector(submissions),
            'by_source_type': {
                'list': by_source_type.get(
                    Source.LIST, {'facilities': 0, 'submissions': 0}
                ),
                'single': by_source_type.get(
                    Source.SINGLE, {'facilities': 0, 'submissions': 0}
                ),
            },
        }

    def list_match_report(self):
        """
        What became of each row of the lists the organization uploaded,
        newest list first: matched to a production location OS Hub
        already had, created a new one, still waiting for the uploader
        to confirm a possible match, failed, repeated another row,
        removed, or not processed yet. The seven counts add up to the
        list's rows.
        """
        lists = list(
            FacilityList.objects
            .filter(
                source__organization=self.organization,
                source__source_type=Source.LIST,
            )
            .select_related('source__contributor__admin')
            .order_by('-created_at')
            [:OrganizationSettings.LIST_MATCH_REPORT_LIMIT]
        )
        if not lists:
            return []

        item = FacilityListItem
        resolved = Q(status__in=(item.MATCHED, item.CONFIRMED_MATCH))
        is_new = Q(facility__created_from_id=F('id'))
        removed = (
            Q(has_removed_match=True)
            | Q(status__in=(item.ITEM_REMOVED, item.DELETED))
        )
        failed_statuses = [
            status for status in item.ERROR_STATUSES
            if status != item.DUPLICATE
        ] + [item.GEOCODED_NO_RESULTS]

        counts = {
            row['source__facility_list_id']: row
            for row in item.objects
            .filter(source__facility_list_id__in=[
                facility_list.id for facility_list in lists
            ])
            .annotate(has_removed_match=Exists(
                FacilityMatch.objects.filter(
                    facility_list_item=OuterRef('pk'), is_active=False
                )
            ))
            .values('source__facility_list_id')
            .annotate(
                total=Count('id'),
                matched_existing=Count(
                    'id', filter=resolved & ~is_new & ~removed
                ),
                new_locations=Count(
                    'id', filter=resolved & is_new & ~removed
                ),
                needs_review=Count(
                    'id', filter=Q(status=item.POTENTIAL_MATCH) & ~removed
                ),
                failed=Count(
                    'id', filter=Q(status__in=failed_statuses) & ~removed
                ),
                duplicates=Count(
                    'id', filter=Q(status=item.DUPLICATE) & ~removed
                ),
                removed=Count('id', filter=removed),
            )
        }

        report = []
        for facility_list in lists:
            row = counts.get(facility_list.id, {})
            source = facility_list.source
            contributor = source.contributor
            total = row.get('total', 0)
            keys = (
                'matched_existing', 'new_locations', 'needs_review',
                'failed', 'duplicates', 'removed',
            )
            numbers = {key: row.get(key, 0) for key in keys}
            report.append({
                'id': facility_list.id,
                'name': facility_list.name,
                'uploaded_at': facility_list.created_at,
                'status': facility_list.status,
                'is_active': source.is_active,
                'submitted_by': {
                    'contributor_id': contributor.id,
                    'contributor_name': contributor.name,
                    'email': contributor.admin.email,
                } if contributor else None,
                'total': total,
                **numbers,
                # Rows still being parsed, geocoded or matched.
                'in_progress': total - sum(numbers.values()),
            })
        return report

    @staticmethod
    def _by_sector(submissions):
        """
        Distinct production locations per sector. A submission can name
        several sectors, so the counts can add up to more than the total.
        """
        return [
            {'sector': row['sector_name'], 'facilities': row['facilities']}
            for row in submissions
            .annotate(sector_name=Func(F('sector'), function='unnest'))
            .values('sector_name')
            .annotate(facilities=Count('facility_id', distinct=True))
            .order_by('-facilities', 'sector_name')
            [:TOP_BREAKDOWN_ROWS]
        ]

    def _pending_moderation_count(self):
        """
        Contributions still waiting for moderation. They have no
        production location yet, so they are counted, not listed.
        """
        queryset = ModerationEvent.objects.filter(
            organization=self.organization,
            status=ModerationEvent.Status.PENDING,
        ).exclude(request_type=ModerationEvent.RequestType.CLAIM)

        member = self.filters.get('member')
        if member:
            queryset = queryset.filter(contributor_id=member)

        return queryset.count()

    def facility_detail(self, os_id):
        """
        One production location the organization submitted: its
        submissions by the organization and its claimed data. Returns
        None when the organization never submitted it.
        """
        rows = list(
            OrganizationDashboardService(self.organization)
            .facility_rows()
            .filter(facility_id=os_id)
        )
        if not rows:
            return None

        facility = rows[0].facility
        index = (
            FacilityIndex.objects
            .filter(id=os_id)
            .only('id', 'claim_info', 'sector')
            .first()
        )

        return {
            'os_id': facility.id,
            'name': facility.name,
            'address': facility.address,
            'country_code': facility.country_code,
            'country_name': COUNTRY_NAMES.get(
                facility.country_code, facility.country_code
            ),
            'sectors': index.sector if index else [],
            'is_claimed': rows[0].is_claimed,
            'claimed_at': rows[0].claimed_at,
            'claim': self._public_claim_info(index),
            'submissions': [self.serialize_row(row) for row in rows],
        }

    @staticmethod
    def _public_claim_info(index):
        """
        The claimed data exactly as the public profile shows it.
        FacilityIndex.claim_info is built by index_claim_info, which
        already leaves out the website, phone, contact and office
        details a claimant chose not to publish. The claimant's user id
        is dropped: the dashboard has no use for it.
        """
        if index is None or not index.claim_info:
            return None

        claim_info = dict(index.claim_info)
        claimant = claim_info.pop('contributor', None) or {}
        claim_info['claimed_by'] = claimant.get('name')
        return claim_info
