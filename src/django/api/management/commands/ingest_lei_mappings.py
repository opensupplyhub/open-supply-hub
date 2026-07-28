import csv
import io
import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from api.constants import ProcessingAction
from api.helpers.helpers import clean
from api.models.contributor.contributor import Contributor
from api.models.extended_field import ExtendedField
from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.lei_mapping import LeiMapping
from api.models.sector import Sector
from api.models.source import Source

LEI_RE = re.compile(r'^[A-Z0-9]{18}\d{2}$')
INGEST_MATCH_TYPE = 'lei_mapping_ingest'
# The canonical admin email of the GLEIF contributor account. The account
# must be created with this email in every environment (see the OSDEV-3095
# runbook notes); ids differ per environment, emails do not.
GLEIF_CONTRIBUTOR_EMAIL = 'gleif-data@opensupplyhub.org'
REQUIRED_COLUMNS = ('os_id', 'lei', 'match_type')
VALID_MATCH_TYPES = (LeiMapping.FACILITY_NAME, LeiMapping.PARENT_COMPANY)
STAT_KEYS = (
    'created',
    'unchanged',
    'skipped_existing',
    'invalid',
    'unknown_os_id',
    'alias_resolved',
    'duplicate_target',
)


class Command(BaseCommand):
    help = (
        'Ingest a GLEIF OS Hub-to-LEI mapping CSV file. Each mapping is '
        'recorded in the LeiMapping ledger and materialized as a '
        'contribution chain (Source, FacilityListItem, FacilityMatch and '
        'a lei_id ExtendedField) attributed to the GLEIF contributor. '
        'Re-running with the same file is a no-op. This command creates '
        'new mappings only; updates, removals and denylist handling arrive '
        'with the monthly-process work (OSDEV-3097). The CSV is OS Hub\'s '
        'normalized internal format; converting GLEIF\'s delivery file '
        'into it is a separate step (OSDEV-3096).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', type=str, required=True,
            help='Path to the GLEIF OS Hub-to-LEI mapping CSV file.'
        )
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='Do not write to DB; just report what would be done.'
        )
        parser.add_argument(
            '--batch-size', type=int, default=500,
            help='Number of mappings written per transaction (default: 500).'
        )

    def handle(self, *args, **options):
        self.stdout.write('Ingesting GLEIF LEI mappings...')

        file_path = options['file']
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        contributor = self._resolve_contributor()

        header, rows = self._read_csv(file_path)

        if dry_run:
            self.stdout.write(self.style.WARNING(
                'DRY-RUN enabled: no database writes will be performed.'
            ))

        stats = {key: 0 for key in STAT_KEYS}
        ledger = {
            mapping.os_id: mapping
            for mapping in LeiMapping.objects.all()
        }
        seen_facility_ids = set()
        creates = []

        for row_number, row in enumerate(rows, start=2):
            plan = self._plan_row(
                row,
                row_number,
                ledger,
                seen_facility_ids,
                stats,
            )
            if plan is not None:
                creates.append(plan)

        stats['created'] = len(creates)

        if not dry_run:
            self._facility_list_source = None
            self._next_row_index = 0
            self._header_str = ','.join(header)
            self._apply_creates(creates, contributor, batch_size)

        self._report(stats, dry_run)

    @staticmethod
    def _resolve_contributor():
        contributor = (
            Contributor
            .objects
            .filter(admin__email__iexact=GLEIF_CONTRIBUTOR_EMAIL)
            .first()
        )
        if contributor is None:
            raise CommandError(
                'No contributor account found for the GLEIF admin email '
                f'{GLEIF_CONTRIBUTOR_EMAIL}. Create the GLEIF contributor '
                'account first.'
            )
        return contributor

    @staticmethod
    def _parse_date(value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _read_csv(file_path):
        try:
            with open(file_path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                if fieldnames is None:
                    raise CommandError(f'The file {file_path} is empty.')
                missing = [
                    column for column in REQUIRED_COLUMNS
                    if column not in fieldnames
                ]
                if missing:
                    raise CommandError(
                        'The CSV file is missing required column(s): '
                        + ', '.join(missing)
                    )
                rows = list(reader)
        except OSError as exc:
            raise CommandError(f'Could not read {file_path}: {exc}')
        return fieldnames, rows

    @staticmethod
    def _resolve_facility(os_id):
        """
        Return (facility, was_alias_resolved) for an OS ID, following
        FacilityAlias to the canonical facility when the OS ID belongs
        to a merged or deleted facility.
        """
        facility = Facility.objects.filter(id=os_id).first()
        if facility is not None:
            return facility, False
        alias = (
            FacilityAlias
            .objects
            .filter(os_id=os_id)
            .select_related('facility')
            .first()
        )
        if alias is not None:
            return alias.facility, True
        return None, False

    def _plan_row(
        self,
        row,
        row_number,
        ledger,
        seen_facility_ids,
        stats,
    ):
        os_id = (row.get('os_id') or '').strip()
        lei = (row.get('lei') or '').strip()
        match_type = (row.get('match_type') or '').strip()

        if not os_id:
            stats['invalid'] += 1
            self.stderr.write(f'Row {row_number}: missing os_id.')
            return None

        if not LEI_RE.fullmatch(lei):
            stats['invalid'] += 1
            self.stderr.write(
                f'Row {row_number}: invalid LEI {lei!r}. It should be a '
                '20-character string with 18 alphanumeric characters '
                'followed by 2 digits.'
            )
            return None

        if match_type not in VALID_MATCH_TYPES:
            stats['invalid'] += 1
            self.stderr.write(
                f'Row {row_number}: invalid match_type {match_type!r}. '
                'Expected one of: ' + ', '.join(VALID_MATCH_TYPES) + '.'
            )
            return None

        # The mapping-file date is optional for now — it is one of the
        # fields still unconfirmed with GLEIF. Stored when provided.
        file_date = None
        raw_date = (row.get('mapping_file_date') or '').strip()
        if raw_date:
            file_date = self._parse_date(raw_date)
            if file_date is None:
                stats['invalid'] += 1
                self.stderr.write(
                    f'Row {row_number}: invalid mapping_file_date '
                    f'{raw_date!r}. Expected YYYY-MM-DD.'
                )
                return None

        facility, was_alias_resolved = self._resolve_facility(os_id)
        if facility is None:
            stats['unknown_os_id'] += 1
            self.stderr.write(
                f'Row {row_number}: unknown OS ID {os_id}; skipping.'
            )
            return None
        if was_alias_resolved:
            stats['alias_resolved'] += 1

        if facility.id in seen_facility_ids:
            stats['duplicate_target'] += 1
            self.stderr.write(
                f'Row {row_number}: OS ID {os_id} resolves to facility '
                f'{facility.id} which an earlier row already mapped; '
                'keeping the first row.'
            )
            return None
        seen_facility_ids.add(facility.id)

        try:
            score = float(row['score'])
        except (KeyError, TypeError, ValueError):
            score = None

        plan = {
            'facility': facility,
            'row': row,
            'lei': lei,
            'match_type': match_type,
            'matched_name': (row.get('matched_name') or '').strip(),
            'score': score,
            'file_date': file_date,
        }

        mapping = ledger.get(facility.id)
        if mapping is not None:
            if (
                mapping.status == LeiMapping.ACTIVE
                and mapping.lei == lei
                and mapping.match_type == match_type
            ):
                stats['unchanged'] += 1
                return None
            # This command only creates mappings for OS IDs new to the
            # ledger. Changed, removed and denylisted mappings are handled
            # by the diff-semantics follow-up (OSDEV-3097).
            stats['skipped_existing'] += 1
            self.stderr.write(self.style.WARNING(
                f'Row {row_number}: facility {facility.id} already has a '
                f'ledger entry ({mapping.status}); skipping — changes are '
                'handled by the diff-semantics follow-up.'
            ))
            return None

        return plan

    def _ensure_source(self, contributor):
        if self._facility_list_source is not None:
            return self._facility_list_source

        ingest_date = timezone.localdate().isoformat()
        list_name = f'GLEIF LEI Mapping — {ingest_date}'
        facility_list = FacilityList.objects.create(
            name=list_name,
            description=(
                'OS Hub-to-LEI mappings provided by GLEIF and ingested by '
                'the ingest_lei_mappings management command.'
            ),
            file_name=f'gleif_lei_mapping_{ingest_date}.csv',
            header=self._header_str,
        )
        self._facility_list_source = Source.objects.create(
            contributor=contributor,
            source_type=Source.LIST,
            facility_list=facility_list,
            is_active=True,
            is_public=True,
            create=False,
        )
        return self._facility_list_source

    def _create_chain(self, plan, contributor):
        """
        Create the FacilityListItem, FacilityMatch and lei_id
        ExtendedField for a single mapping, mirroring the state the
        moderation event approval flow leaves behind for an already
        known facility. No geocoding or matching is triggered.
        """
        facility = plan['facility']
        row = plan['row']
        source = self._ensure_source(contributor)

        name = facility.name
        address = facility.address
        now = str(timezone.now())

        item = FacilityListItem.objects.create(
            source=source,
            row_index=self._next_row_index,
            raw_data=self._csv_line(row),
            raw_json={
                column: row.get(column) or ''
                for column in self._header_str.split(',')
            },
            raw_header=self._header_str,
            name=name[:200],
            clean_name=clean(name[:200]) or '',
            address=address[:200],
            clean_address=clean(address[:200]) or '',
            country_code=facility.country_code,
            sector=[Sector.DEFAULT_SECTOR_NAME],
            status=FacilityListItem.CONFIRMED_MATCH,
            facility=facility,
            processing_results=[
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': now,
                    'error': False,
                    'finished_at': now,
                    'is_geocoded': False,
                },
                {
                    'action': ProcessingAction.MATCH,
                    'started_at': now,
                    'error': False,
                    'finished_at': now,
                },
            ],
        )
        self._next_row_index += 1

        FacilityMatch.objects.create(
            facility=facility,
            facility_list_item=item,
            confidence=1.0,
            status=FacilityMatch.CONFIRMED,
            is_active=True,
            results={'match_type': INGEST_MATCH_TYPE},
        )

        ExtendedField.objects.create(
            contributor=contributor,
            facility=facility,
            facility_list_item=item,
            field_name=ExtendedField.LEI_ID,
            value={
                'raw_value': plan['lei'],
                'match_type': plan['match_type'],
            },
        )

    def _save_ledger_row(self, plan):
        LeiMapping.objects.create(
            os_id=plan['facility'].id,
            lei=plan['lei'],
            match_type=plan['match_type'],
            matched_name=plan['matched_name'],
            score=plan['score'],
            mapping_file_date=plan['file_date'],
            status=LeiMapping.ACTIVE,
        )

    def _csv_line(self, row):
        buffer = io.StringIO()
        csv.writer(buffer).writerow([
            row.get(column) or ''
            for column in self._header_str.split(',')
        ])
        return buffer.getvalue().rstrip('\r\n')

    @staticmethod
    def _batches(items, batch_size):
        for start in range(0, len(items), batch_size):
            yield items[start:start + batch_size]

    def _apply_creates(self, creates, contributor, batch_size):
        for batch in self._batches(creates, batch_size):
            with transaction.atomic():
                for plan in batch:
                    self._create_chain(plan, contributor)
                    self._save_ledger_row(plan)

    def _report(self, stats, dry_run):
        summary = ' '.join(
            f'{key}={stats[key]}' for key in STAT_KEYS
        )
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'Done [DRY-RUN]. No changes written. {summary}'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f'Done. {summary}'))
