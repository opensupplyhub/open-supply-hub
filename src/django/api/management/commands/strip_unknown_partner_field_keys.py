from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models.extended_field import ExtendedField
from api.models.partner_field import PartnerField
from api.models.transactions.index_facilities_new import (
    index_facilities_new,
)
from api.serializers.facility.partner_field_helper import (
    filter_value_to_schema,
)


class Command(BaseCommand):
    help = (
        "Strip keys that are not declared in a partner field's JSON Schema "
        "from the stored ExtendedField.value.raw_values. This removes "
        "contributor-supplied extras (e.g. an internal_ID) that were "
        "persisted before schema-based output filtering was in place, and "
        "reindexes the affected facilities so the search index no longer "
        "carries the stripped values."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size', type=int, default=1000,
            help='Number of rows to load per chunk (default: 1000)'
        )
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='Do not write to DB or reindex; just report what would change'
        )
        parser.add_argument(
            '--field-name', type=str, default=None,
            help='Restrict to a single partner field name'
        )
        parser.add_argument(
            '--no-reindex', action='store_false', dest='reindex',
            default=True,
            help='Skip reindexing the affected facilities'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        field_name_filter = options['field_name']
        should_reindex = options['reindex']

        if dry_run:
            self.stdout.write(self.style.WARNING(
                'DRY-RUN enabled: no database writes or reindexing.'
            ))

        schemas = self._object_field_schemas(field_name_filter)
        if not schemas:
            self.stdout.write(
                'No object-typed partner fields with a JSON Schema found; '
                'nothing to do.'
            )
            return

        rows_qs = (
            ExtendedField.objects
            .filter(field_name__in=schemas.keys())
            .order_by('id')
        )

        stats = {
            'scanned': 0,
            'updated': 0,
            'unchanged': 0,
        }
        affected_facility_ids = set()
        last_log = timezone.now()

        for field in rows_qs.iterator(chunk_size=batch_size):
            stats['scanned'] += 1
            value = field.value
            if not isinstance(value, dict):
                stats['unchanged'] += 1
                continue

            raw_values = value.get('raw_values')
            if not isinstance(raw_values, dict):
                stats['unchanged'] += 1
                continue

            filtered = filter_value_to_schema(
                raw_values,
                schemas[field.field_name],
            )
            if filtered == raw_values:
                stats['unchanged'] += 1
                continue

            stats['updated'] += 1
            if field.facility_id:
                affected_facility_ids.add(field.facility_id)

            if dry_run:
                removed = sorted(
                    set(raw_values.keys()) - set(filtered.keys())
                )
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY-RUN] Would strip {removed} from "
                        f"ExtendedField id={field.id} "
                        f"(field_name={field.field_name})"
                    )
                )
            else:
                value['raw_values'] = filtered
                with transaction.atomic():
                    ExtendedField.objects.filter(id=field.id).update(
                        value=value
                    )

            now = timezone.now()
            if (now - last_log).total_seconds() >= 10:
                self.stdout.write(
                    f"Progress: scanned={stats['scanned']} "
                    f"updated={stats['updated']} "
                    f"unchanged={stats['unchanged']}"
                )
                last_log = now

        if should_reindex and affected_facility_ids and not dry_run:
            self.stdout.write(
                f"Reindexing {len(affected_facility_ids)} facility(ies)..."
            )
            index_facilities_new(list(affected_facility_ids))

        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(style(
            "Done. "
            f"scanned={stats['scanned']} "
            f"updated={stats['updated']} "
            f"unchanged={stats['unchanged']} "
            f"affected_facilities={len(affected_facility_ids)}"
        ))

    @staticmethod
    def _object_field_schemas(field_name_filter):
        qs = PartnerField.objects.get_all_including_inactive().filter(
            type=PartnerField.OBJECT,
        )
        if field_name_filter:
            qs = qs.filter(name=field_name_filter)

        return {
            field.name: field.json_schema
            for field in qs
            if isinstance(field.json_schema, dict)
            and field.json_schema.get('properties')
        }
