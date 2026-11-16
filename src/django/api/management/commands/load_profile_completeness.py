import csv
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Facility, FacilityProfileCompleteness
from api.profile_completeness import COMPONENT_KEYS, ClassifierTiers


SCORE_ID_COLUMN = 'facility_id'
SCORE_COLUMN = 'final_data_quality_score'

CLASSIFIER_ID_COLUMN = 'os_id'
CLASSIFIER_TIER_COLUMN = 'final_tier'
CLASSIFIER_AGREEMENT_COLUMN = 'A_tier'
CLASSIFIER_FIELD_COLUMN = 'B_tier'
CLASSIFIER_MODEL_COLUMN = 'model'


BATCH_SIZE = 5000


def _read_rows(path, required_columns):
    '''Yield the file's rows one at a time, so a whole-population file
    is never held in memory.'''
    try:
        with open(path, newline='', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            missing = [
                column for column in required_columns
                if column not in (reader.fieldnames or [])
            ]
            if missing:
                raise CommandError(
                    f'{path} is missing the column(s): '
                    f'{", ".join(missing)}.'
                )
            yield from reader
    except OSError as error:
        raise CommandError(str(error)) from error


def _batches(rows):
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) == BATCH_SIZE:
            yield batch
            batch = []
    if batch:
        yield batch


def _unit_interval(value, column, os_id):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise CommandError(
            f'{os_id}: {column} is not a number ({value!r}).'
        )
    if not 0 <= number <= 1:
        raise CommandError(
            f'{os_id}: {column} is outside 0 to 1 ({number}).'
        )
    return number


def _tier(value, allowed, column, os_id):
    tier = (value or '').strip().lower()
    if tier not in allowed:
        raise CommandError(
            f'{os_id}: {column} is {value!r}, expected one of '
            f'{", ".join(allowed)}.'
        )
    return tier


class Command(BaseCommand):
    help = (
        'Load one run of profile completeness readings: the scorer output '
        '(--scores-file) and/or the model-backed classification '
        '(--classifier-file). Rows are stored per production location and '
        'run date; loading the same run date again updates them. OS IDs '
        'that do not exist in this database are skipped and counted.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--scores-file',
            help=(
                'CSV as the scorer writes it: facility_id, '
                'final_data_quality_score and one column per component.'
            ),
        )
        parser.add_argument(
            '--scorer-version',
            default='',
            help='Version of the scorer that produced --scores-file.',
        )
        parser.add_argument(
            '--classifier-file',
            help=(
                'CSV of the classification: os_id, final_tier, A_tier, '
                'B_tier and model.'
            ),
        )
        parser.add_argument(
            '--run-date',
            type=date.fromisoformat,
            default=None,
            help='YYYY-MM-DD the readings were computed. Default: today.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate the file(s) without changing the table.',
        )

    def handle(self, *args, **options):
        if not options['scores_file'] and not options['classifier_file']:
            raise CommandError(
                'Give --scores-file, --classifier-file or both.'
            )

        run_date = options['run_date'] or date.today()
        dry_run = options['dry_run']
        sources = []
        if options['scores_file']:
            sources.append((
                'scores',
                self._score_rows(
                    options['scores_file'], options['scorer_version'],
                ),
                ('score', 'components', 'scorer_version'),
            ))
        if options['classifier_file']:
            sources.append((
                'classifications',
                self._classifier_rows(options['classifier_file']),
                (
                    'classifier_tier',
                    'classifier_agreement_tier',
                    'classifier_field_tier',
                    'classifier_model',
                ),
            ))

        # One transaction, so a bad row late in a file leaves nothing
        # half-loaded.
        with transaction.atomic():
            for label, rows, fields in sources:
                loaded, skipped = self._load(rows, fields, run_date, dry_run)
                self.stdout.write(
                    f'{label}: {loaded + len(skipped)} rows are valid; '
                    f'{loaded} match a production location here, '
                    f'{len(skipped)} do not.'
                )
                if skipped:
                    self.stdout.write(
                        'Not found: ' + ', '.join(skipped[:20])
                        + (' ...' if len(skipped) > 20 else '')
                    )

        if dry_run:
            self.stdout.write('Nothing was changed.')
        else:
            self.stdout.write(self.style.SUCCESS(f'Loaded for {run_date}.'))

    @staticmethod
    def _load(rows, fields, run_date, dry_run):
        '''
        Upsert one file's rows a batch at a time, writing only that
        file's fields so loading scores never clears a classification
        already stored for the same run date, and the reverse.
        '''
        loaded = 0
        skipped = []
        for batch in _batches(rows):
            values_by_id = dict(batch)
            known_ids = set(
                Facility.objects
                .filter(id__in=values_by_id.keys())
                .values_list('id', flat=True)
            )
            skipped.extend(sorted(set(values_by_id) - known_ids))
            loaded += len(known_ids)
            if dry_run:
                continue
            FacilityProfileCompleteness.objects.bulk_create(
                [
                    FacilityProfileCompleteness(
                        facility_id=os_id,
                        run_date=run_date,
                        **values_by_id[os_id],
                    )
                    for os_id in sorted(known_ids)
                ],
                update_conflicts=True,
                unique_fields=('facility', 'run_date'),
                update_fields=fields + ('updated_at',),
            )
        return loaded, skipped

    @staticmethod
    def _score_rows(path, scorer_version):
        rows = _read_rows(
            path, (SCORE_ID_COLUMN, SCORE_COLUMN) + COMPONENT_KEYS,
        )
        for row in rows:
            os_id = row[SCORE_ID_COLUMN].strip()
            yield os_id, {
                'score': _unit_interval(
                    row[SCORE_COLUMN], SCORE_COLUMN, os_id,
                ),
                'components': {
                    key: _unit_interval(row[key], key, os_id)
                    for key in COMPONENT_KEYS
                },
                'scorer_version': scorer_version,
            }

    @staticmethod
    def _classifier_rows(path):
        rows = _read_rows(path, (
            CLASSIFIER_ID_COLUMN,
            CLASSIFIER_TIER_COLUMN,
            CLASSIFIER_AGREEMENT_COLUMN,
            CLASSIFIER_FIELD_COLUMN,
            CLASSIFIER_MODEL_COLUMN,
        ))
        for row in rows:
            os_id = row[CLASSIFIER_ID_COLUMN].strip()
            yield os_id, {
                'classifier_tier': _tier(
                    row[CLASSIFIER_TIER_COLUMN],
                    ClassifierTiers.FINAL,
                    CLASSIFIER_TIER_COLUMN,
                    os_id,
                ),
                'classifier_agreement_tier': _tier(
                    row[CLASSIFIER_AGREEMENT_COLUMN],
                    ClassifierTiers.AGREEMENT,
                    CLASSIFIER_AGREEMENT_COLUMN,
                    os_id,
                ),
                'classifier_field_tier': _tier(
                    row[CLASSIFIER_FIELD_COLUMN],
                    ClassifierTiers.FINAL,
                    CLASSIFIER_FIELD_COLUMN,
                    os_id,
                ),
                'classifier_model': row[CLASSIFIER_MODEL_COLUMN].strip(),
            }
