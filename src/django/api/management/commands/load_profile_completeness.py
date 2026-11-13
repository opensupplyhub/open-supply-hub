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


def _read_rows(path, required_columns):
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
            return list(reader)
    except OSError as error:
        raise CommandError(str(error)) from error


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

        updates = {}
        if options['scores_file']:
            self._collect_scores(
                updates, options['scores_file'], options['scorer_version'],
            )
        if options['classifier_file']:
            self._collect_classifications(
                updates, options['classifier_file'],
            )

        known_ids = set(
            Facility.objects
            .filter(id__in=updates.keys())
            .values_list('id', flat=True)
        )
        skipped = sorted(set(updates) - known_ids)
        run_date = options['run_date'] or date.today()

        if options['dry_run']:
            self.stdout.write(
                f'{len(updates)} rows are valid; {len(known_ids)} match a '
                f'production location here, {len(skipped)} do not. '
                'Nothing was changed.'
            )
            return

        with transaction.atomic():
            for os_id in sorted(known_ids):
                FacilityProfileCompleteness.objects.update_or_create(
                    facility_id=os_id,
                    run_date=run_date,
                    defaults=updates[os_id],
                )

        self.stdout.write(self.style.SUCCESS(
            f'Loaded {len(known_ids)} rows for {run_date}; skipped '
            f'{len(skipped)} OS IDs not in this database.'
        ))
        if skipped:
            self.stdout.write('Skipped: ' + ', '.join(skipped[:20]) + (
                ' ...' if len(skipped) > 20 else ''
            ))

    @staticmethod
    def _collect_scores(updates, path, scorer_version):
        rows = _read_rows(
            path, (SCORE_ID_COLUMN, SCORE_COLUMN) + COMPONENT_KEYS,
        )
        for row in rows:
            os_id = row[SCORE_ID_COLUMN].strip()
            updates.setdefault(os_id, {}).update({
                'score': _unit_interval(
                    row[SCORE_COLUMN], SCORE_COLUMN, os_id,
                ),
                'components': {
                    key: _unit_interval(row[key], key, os_id)
                    for key in COMPONENT_KEYS
                },
                'scorer_version': scorer_version,
            })

    @staticmethod
    def _collect_classifications(updates, path):
        rows = _read_rows(path, (
            CLASSIFIER_ID_COLUMN,
            CLASSIFIER_TIER_COLUMN,
            CLASSIFIER_AGREEMENT_COLUMN,
            CLASSIFIER_FIELD_COLUMN,
            CLASSIFIER_MODEL_COLUMN,
        ))
        for row in rows:
            os_id = row[CLASSIFIER_ID_COLUMN].strip()
            updates.setdefault(os_id, {}).update({
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
            })
