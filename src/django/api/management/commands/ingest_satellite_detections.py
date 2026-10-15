"""
Ingest Earth Genome satellite detections as candidate facilities
(OSDEV-3244, design decisions D1, D2 and D5).

Every detection becomes a real ``api_facility`` row with an OS ID,
``is_candidate=True``, the detected ``polygon`` and ``confidence``, and the
empty-string sentinel for ``name`` and ``address`` (D1). Each row is
created the way SLC approval creates a facility (D2): a synthetic
``SINGLE`` ``Source`` owned by the Earth Genome contributor, a ``MATCHED``
``FacilityListItem`` carrying the full detection payload in
``raw_json``, and an ``AUTOMATIC`` ``FacilityMatch``. No schema change is
involved.

Idempotency keys on ``(source, external_id)``: a detection that already
has a facility is updated in place (polygon, confidence, location,
payload) and keeps its OS ID; a detection retired as NOT_A_FACILITY is
never re-created (D5, ``api.services.candidate_retirement``).

Two input formats are accepted:

* the prototype JSON list (``nc_candidates.json``): records with
  ``eg_id``, ``polygon`` (GeoJSON geometry), ``centroid_lat`` /
  ``centroid_lng``, ``probable_facility_type``, ``confidence_score`` and
  ``eg_model_version``;
* a GeoJSON ``FeatureCollection`` as exported by Earth Genome: features
  with a ``Polygon`` geometry (``null`` for a detection without a
  footprint, which is skipped) and ``properties.id`` /
  ``properties.confidence``.

Usage::

    python manage.py ingest_satellite_detections --file detections.geojson
        [--source earth_genome] [--country-code US] [--limit N] [--dry-run]
"""
import json
import os
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from api.constants import ProcessingAction
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.sector import Sector
from api.models.source import Source
from api.services.candidate_matches import (
    suggested_matches,
    suggested_matches_for_point,
)
from api.services.candidate_retirement import is_retired_detection
from countries.lib.countries import COUNTRY_CHOICES

DEFAULT_SOURCE = 'earth_genome'
DEFAULT_COUNTRY_CODE = 'US'

# The sector recorded on the synthetic list item when the detection's
# facility type is not itself a known Sector name.
DEFAULT_CANDIDATE_SECTOR = 'Agriculture'
# Earth Genome facility types that map onto an existing Sector name. The
# mapped name is only used when the Sector table actually contains it.
FACILITY_TYPE_SECTORS = {
    'poultry': 'Animal Production',
}

MATCH_TYPE = 'satellite_detection_candidate'

VALID_COUNTRY_CODES = {code for code, _ in COUNTRY_CHOICES}


class DetectionError(ValueError):
    """A single detection could not be read; the run continues."""


@dataclass
class Detection:
    external_id: str
    polygon: Optional[Polygon]
    centroid: Point
    confidence: Optional[float]
    facility_type: str
    model_version: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def payload(self, source):
        """The provenance stored in ``FacilityListItem.raw_json``."""
        return {
            'source': source,
            'external_id': self.external_id,
            'confidence': self.confidence,
            'probable_facility_type': self.facility_type,
            'eg_model_version': self.model_version,
            'centroid_lat': self.centroid.y,
            'centroid_lng': self.centroid.x,
            'polygon': (
                json.loads(self.polygon.geojson) if self.polygon else None
            ),
            'properties': self.properties,
        }


@dataclass
class Summary:
    created: int = 0
    updated: int = 0
    skipped_retired: int = 0
    skipped_no_geometry: int = 0
    errors: int = 0
    with_suggestions: int = 0
    suggestions: int = 0

    def line(self):
        return (
            f'created={self.created} updated={self.updated} '
            f'skipped_retired={self.skipped_retired} '
            f'skipped_no_geometry={self.skipped_no_geometry} '
            f'errors={self.errors} '
            f'with_suggestions={self.with_suggestions} '
            f'(suggestions={self.suggestions})'
        )


# --- input parsing ---------------------------------------------------------


def _as_polygon(geometry, external_id):
    """GeoJSON geometry dict (or None) -> Polygon with SRID 4326, or None."""
    if geometry is None:
        return None
    try:
        geom = GEOSGeometry(json.dumps(geometry), srid=4326)
    except Exception as exc:
        raise DetectionError(
            f'{external_id}: unreadable geometry ({exc})'
        ) from exc
    if geom.empty:
        return None
    if geom.geom_type == 'MultiPolygon' and len(geom) == 1:
        geom = geom[0]
        geom.srid = 4326
    if geom.geom_type != 'Polygon':
        raise DetectionError(
            f'{external_id}: geometry must be a Polygon, got '
            f'{geom.geom_type}'
        )
    if not geom.valid:
        raise DetectionError(
            f'{external_id}: invalid polygon ({geom.valid_reason})'
        )
    return geom


def _as_float(value, external_id, label):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise DetectionError(
            f'{external_id}: {label} is not a number ({value!r})'
        ) from exc


def _require_external_id(value, position):
    if value is None or str(value).strip() == '':
        raise DetectionError(f'record #{position}: missing external id')
    return str(value).strip()


def _from_prototype_record(record, position):
    """``nc_candidates.json`` record -> Detection (None without geometry)."""
    if not isinstance(record, dict):
        raise DetectionError(f'record #{position}: not an object')
    external_id = _require_external_id(record.get('eg_id'), position)
    polygon = _as_polygon(record.get('polygon'), external_id)

    lat = _as_float(record.get('centroid_lat'), external_id, 'centroid_lat')
    lng = _as_float(record.get('centroid_lng'), external_id, 'centroid_lng')
    if lat is not None and lng is not None:
        centroid = Point(lng, lat, srid=4326)
    elif polygon is not None:
        centroid = polygon.centroid
        centroid.srid = 4326
    else:
        return None

    properties = {
        key: value for key, value in record.items() if key != 'polygon'
    }
    return Detection(
        external_id=external_id,
        polygon=polygon,
        centroid=centroid,
        confidence=_as_float(
            record.get('confidence_score'), external_id, 'confidence_score'
        ),
        facility_type=str(record.get('probable_facility_type') or ''),
        model_version=str(record.get('eg_model_version') or ''),
        properties=properties,
    )


def _from_feature(feature, position):
    """GeoJSON Feature -> Detection (None when geometry is null)."""
    if not isinstance(feature, dict) or feature.get('type') != 'Feature':
        raise DetectionError(f'feature #{position}: not a GeoJSON Feature')
    properties = feature.get('properties') or {}
    external_id = _require_external_id(
        properties.get('id', feature.get('id')), position
    )
    polygon = _as_polygon(feature.get('geometry'), external_id)
    if polygon is None:
        return None
    centroid = polygon.centroid
    centroid.srid = 4326
    return Detection(
        external_id=external_id,
        polygon=polygon,
        centroid=centroid,
        confidence=_as_float(
            properties.get('confidence'), external_id, 'confidence'
        ),
        facility_type=str(
            properties.get('probable_facility_type')
            or properties.get('facility_type')
            or ''
        ),
        model_version=str(
            properties.get('eg_model_version')
            or properties.get('model_version')
            or ''
        ),
        properties=properties,
    )


def load_records(path):
    """
    Read ``path`` and return ``(records, parser)`` where ``parser`` turns
    one record into a Detection.
    """
    with open(path) as handle:
        try:
            data = json.load(handle)
        except ValueError as exc:
            raise CommandError(f'{path}: not valid JSON ({exc})') from exc

    if isinstance(data, dict) and data.get('type') == 'FeatureCollection':
        return list(data.get('features') or []), _from_feature
    if isinstance(data, list):
        return data, _from_prototype_record
    raise CommandError(
        f'{path}: expected a GeoJSON FeatureCollection or a JSON list of '
        'detection records'
    )


# --- command ---------------------------------------------------------------


class Command(BaseCommand):
    help = (
        'Ingest Earth Genome satellite detections as candidate facilities '
        '(is_candidate=True) under the Earth Genome contributor. Idempotent '
        'on (source, external_id); retired detections are never re-created.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            required=True,
            help=(
                'Path to the detections: a GeoJSON FeatureCollection as '
                'exported by Earth Genome, or the prototype JSON list '
                '(nc_candidates.json format).'
            ),
        )
        parser.add_argument(
            '--source',
            default=DEFAULT_SOURCE,
            help=(
                'Value stored in Facility.source; half of the idempotency '
                f'key (default: {DEFAULT_SOURCE}).'
            ),
        )
        parser.add_argument(
            '--country-code',
            default=DEFAULT_COUNTRY_CODE,
            help=(
                'ISO 3166-1 alpha-2 country code recorded on every '
                'candidate and used to mint its OS ID. There is no offline '
                'point-to-country lookup yet, so the whole file must come '
                f'from one country (default: {DEFAULT_COUNTRY_CODE}).'
            ),
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Stop after this many records from the file.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=(
                'Parse and classify every detection (create / update / '
                'skip) and list proximity suggestions, but write nothing.'
            ),
        )

    def handle(self, *args, **options):
        path = os.path.abspath(options['file'])
        if not os.path.isfile(path):
            raise CommandError(f'No such file: {path}')

        source = (options['source'] or '').strip()
        if not source:
            raise CommandError('--source must not be empty')

        country_code = (options['country_code'] or '').strip().upper()
        if country_code not in VALID_COUNTRY_CODES:
            raise CommandError(
                f'--country-code {options["country_code"]!r} is not an '
                'ISO 3166-1 alpha-2 country code'
            )

        dry_run = options['dry_run']
        verbose = dry_run or options['verbosity'] >= 2
        contributor = self._resolve_contributor()

        records, parse = load_records(path)
        if options['limit'] is not None:
            records = records[: options['limit']]

        self.stdout.write(
            f'{"Dry run: " if dry_run else ""}ingesting {len(records)} '
            f'record(s) from {path} as source={source!r} '
            f'country_code={country_code!r} under contributor '
            f'{contributor.id} ({contributor.name})'
        )

        summary = Summary()
        for position, record in enumerate(records, start=1):
            try:
                detection = parse(record, position)
            except DetectionError as exc:
                summary.errors += 1
                self.stderr.write(f'ERROR {exc}')
                continue
            if detection is None:
                summary.skipped_no_geometry += 1
                if verbose:
                    self.stdout.write(
                        f'SKIP (no geometry) record #{position}'
                    )
                continue

            try:
                self._ingest(
                    detection, source, country_code, contributor,
                    dry_run, verbose, summary,
                )
            except Exception as exc:  # one bad row must not stop the run
                summary.errors += 1
                self.stderr.write(
                    f'ERROR {detection.external_id}: '
                    f'{exc.__class__.__name__}: {exc}'
                )

        line = summary.line()
        if summary.errors:
            raise CommandError(f'Finished with errors: {line}')
        self.stdout.write(self.style.SUCCESS(f'Done: {line}'))

    # --- helpers ---------------------------------------------------------

    def _resolve_contributor(self):
        """
        The Earth Genome contributor from settings.EARTH_GENOME_CONTRIBUTOR_ID.

        Facility.save() would reject every candidate anyway without it
        (OSDEV-3248); failing here gives one clear message instead of one
        error per detection.
        """
        contributor_id = settings.EARTH_GENOME_CONTRIBUTOR_ID
        if contributor_id is None:
            raise CommandError(
                'EARTH_GENOME_CONTRIBUTOR_ID is not set. Set it to the id '
                'of the Earth Genome contributor; only that contributor '
                'may create candidate facilities (OSDEV-3248).'
            )
        try:
            return Contributor.objects.get(id=contributor_id)
        except Contributor.DoesNotExist:
            raise CommandError(
                f'EARTH_GENOME_CONTRIBUTOR_ID={contributor_id} does not '
                'match any Contributor.'
            ) from None

    def _ingest(
        self, detection, source, country_code, contributor,
        dry_run, verbose, summary,
    ):
        external_id = detection.external_id
        if is_retired_detection(source, external_id):
            summary.skipped_retired += 1
            if verbose:
                self.stdout.write(f'SKIP (retired) {external_id}')
            return

        existing = Facility.including_candidates.filter(
            source=source, external_id=external_id
        ).first()

        if dry_run:
            action = 'UPDATE' if existing else 'CREATE'
            os_id = existing.id if existing else '(new OS ID)'
            if existing:
                summary.updated += 1
            else:
                summary.created += 1
            suggestions = suggested_matches_for_point(
                detection.centroid,
                exclude_os_id=existing.id if existing else None,
            )
        else:
            with transaction.atomic():
                if existing:
                    facility = self._update(existing, detection, source)
                    action = 'UPDATE'
                    summary.updated += 1
                else:
                    facility = self._create(
                        detection, source, country_code, contributor
                    )
                    action = 'CREATE'
                    summary.created += 1
            os_id = facility.id
            suggestions = suggested_matches(facility)

        if suggestions:
            summary.with_suggestions += 1
            summary.suggestions += len(suggestions)
        if verbose:
            self.stdout.write(
                f'{action} {external_id} -> {os_id} '
                f'confidence={detection.confidence} '
                f'suggestions={len(suggestions)}'
            )
            for row in suggestions:
                self.stdout.write(
                    f'    {row["os_id"]} {row["distance_m"]} m '
                    f'{row["name"]!r} {row["address"]!r}'
                )

    @staticmethod
    def _sector_for(detection):
        """A list of one sector name for the synthetic list item."""
        wanted = [
            name for name in (
                FACILITY_TYPE_SECTORS.get(detection.facility_type.lower()),
                detection.facility_type.strip(),
            ) if name
        ]
        if wanted:
            known = set(
                Sector.objects.filter(name__in=wanted)
                .values_list('name', flat=True)
            )
            for name in wanted:
                if name in known:
                    return [name]
        return [DEFAULT_CANDIDATE_SECTOR]

    @staticmethod
    def _match_confidence(detection):
        if detection.confidence is None:
            return Decimal('0.00')
        return Decimal(str(round(detection.confidence, 2)))

    @staticmethod
    def _raw_row(payload):
        """``raw_header`` / ``raw_data`` the way the SLC approval path
        builds them: scalar payload values as a quoted CSV-ish line."""
        scalars = {
            key: value for key, value in payload.items()
            if key not in ('polygon', 'properties')
        }
        header = ','.join(scalars.keys())
        row = ','.join(f'"{value}"' for value in scalars.values())
        return header, row

    def _create(self, detection, source, country_code, contributor):
        payload = detection.payload(source)
        raw_header, raw_data = self._raw_row(payload)
        now = str(timezone.now())

        item_source = Source.objects.create(
            contributor=contributor,
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
        )
        item = FacilityListItem.objects.create(
            source=item_source,
            row_index=0,
            raw_data=raw_data,
            raw_header=raw_header,
            raw_json=payload,
            name='',
            address='',
            country_code=country_code,
            sector=self._sector_for(detection),
            geocoded_point=detection.centroid,
            status=FacilityListItem.MATCHED,
            processing_results=[
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': now,
                    'error': False,
                    'finished_at': now,
                    'is_geocoded': True,
                },
                {
                    'action': ProcessingAction.GEOCODE,
                    'started_at': now,
                    'error': False,
                    'skipped_geocoder': True,
                    'finished_at': now,
                },
            ],
        )
        facility = Facility.including_candidates.create(
            name='',
            address='',
            country_code=country_code,
            location=detection.centroid,
            created_from=item,
            is_candidate=True,
            polygon=detection.polygon,
            confidence=detection.confidence,
            external_id=detection.external_id,
            source=source,
        )
        FacilityMatch.objects.create(
            facility=facility,
            facility_list_item=item,
            status=FacilityMatch.AUTOMATIC,
            confidence=self._match_confidence(detection),
            results={
                'match_type': MATCH_TYPE,
                'source': source,
                'external_id': detection.external_id,
                'eg_model_version': detection.model_version,
            },
            is_active=True,
        )
        item.facility = facility
        item.processing_results.append({
            'action': ProcessingAction.MATCH,
            'started_at': now,
            'error': False,
            'finished_at': now,
        })
        item.save()
        return facility

    def _update(self, facility, detection, source):
        """
        Refresh an existing detection's facility in place. Never touches
        ``is_candidate``: a candidate the community has since confirmed
        stays confirmed, and its OS ID is stable across re-ingests.
        """
        payload = detection.payload(source)
        raw_header, raw_data = self._raw_row(payload)

        facility.polygon = detection.polygon
        facility.confidence = detection.confidence
        facility.location = detection.centroid
        facility.save(
            update_fields=['polygon', 'confidence', 'location', 'updated_at']
        )

        item = facility.created_from
        item.raw_json = payload
        item.raw_data = raw_data
        item.raw_header = raw_header
        item.geocoded_point = detection.centroid
        item.save(
            update_fields=[
                'raw_json', 'raw_data', 'raw_header', 'geocoded_point',
                'updated_at',
            ]
        )

        FacilityMatch.objects.filter(
            facility=facility, facility_list_item=item
        ).update(
            confidence=self._match_confidence(detection),
            updated_at=timezone.now(),
        )
        return facility
