from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from api.isic_taxonomy.builder import build_taxonomy, count_taxonomy_levels
from api.isic_taxonomy.errors import (
    IsicTaxonomyPublishError,
    IsicTaxonomyValidationError,
)
from api.isic_taxonomy.generator import generate_js_bundle, generate_json
from api.isic_taxonomy.parser import parse_spreadsheet
from api.isic_taxonomy.publisher import parse_and_validate, publish_taxonomy
from api.isic_taxonomy.validator import validate_file
from api.models.isic_taxonomy_config import IsicTaxonomyConfig

FULL_CSV_HEADER = (
    'section,section_label,division,division_label,group,group_label,'
    'class,full_code,description,4-digits,4-digits classification\n'
)

SAMPLE_CSV = (
    FULL_CSV_HEADER
    + (
        'A,Agriculture,1,Crops,11,Crops,111,A0111,'
        'Growing of cereals,0111,0111\n'
    )
).encode('utf-8')


class IsicTaxonomyParserTest(TestCase):
    def test_parse_and_validate_builds_taxonomy_with_derived_codes(self):
        taxonomy = parse_and_validate(SAMPLE_CSV, 'sample.csv')

        counts = count_taxonomy_levels(taxonomy)
        self.assertEqual(counts['class_count'], 1)

        section = taxonomy['sections'][0]
        cereal = section['divisions'][0]['groups'][0]['classes'][0]
        self.assertEqual(cereal['code'], '0111')
        self.assertEqual(cereal['divisionCode'], '01')
        self.assertEqual(cereal['groupCode'], '011')

    def test_parse_and_validate_rejects_missing_headers(self):
        csv_content = b'section,division\nA,1\n'
        with self.assertRaises(IsicTaxonomyValidationError) as exc:
            validate_file(csv_content, 'bad.csv')

        self.assertIn('Missing required column', str(exc.exception))

    def test_parse_and_validate_rejects_non_utf8_csv(self):
        csv_content = 'section,section_label\nA,\xe9\n'.encode('latin-1')
        with self.assertRaises(IsicTaxonomyValidationError) as exc:
            parse_spreadsheet(csv_content, 'bad.csv')

        self.assertIn('UTF-8', str(exc.exception))

    def test_parse_and_validate_rejects_duplicate_class_codes(self):
        csv_content = (
            FULL_CSV_HEADER
            + 'A,Agriculture,1,Crops,11,Crops,111,A0111,First,0111,0111\n'
            + 'A,Agriculture,1,Crops,11,Crops,111,A0111,Second,0111,0111\n'
        ).encode('utf-8')
        with self.assertRaises(IsicTaxonomyValidationError) as exc:
            validate_file(csv_content, 'duplicate.csv')

        self.assertIn('Duplicate class code "0111"', str(exc.exception))

    def test_parse_and_validate_rejects_mismatched_division_column(self):
        csv_content = (
            FULL_CSV_HEADER
            + (
                'H,Transport,51,Air,521,Warehousing,5210,H5210,'
                'Warehousing,5210,5210\n'
            )
        ).encode('utf-8')
        with self.assertRaises(IsicTaxonomyValidationError) as exc:
            validate_file(csv_content, 'mismatch.csv')

        self.assertIn(
            'does not match the first two digits',
            str(exc.exception),
        )

    def test_parse_and_validate_rejects_disallowed_characters(self):
        csv_content = (
            FULL_CSV_HEADER
            + (
                'A,Agriculture,1,Crops,11,Crops,111,A0111,'
                'Bad\u2603 label,0111,0111\n'
            )
        ).encode('utf-8')
        with self.assertRaises(IsicTaxonomyValidationError) as exc:
            validate_file(csv_content, 'bad-chars.csv')

        self.assertIn('disallowed characters', str(exc.exception).lower())

    def test_generators_emit_expected_artifacts(self):
        taxonomy = build_taxonomy(validate_file(SAMPLE_CSV, 'sample.csv'))

        json_body = generate_json(taxonomy)
        js_body = generate_js_bundle(taxonomy).decode('utf-8')

        self.assertIn(b'"sections"', json_body)
        self.assertTrue(js_body.startswith('export const ISIC_REV4_TAXONOMY'))
        self.assertIn('0111', js_body)

    def test_count_taxonomy_levels(self):
        taxonomy = parse_and_validate(SAMPLE_CSV, 'sample.csv')

        counts = count_taxonomy_levels(taxonomy)
        self.assertEqual(counts, {
            'section_count': 1,
            'division_count': 1,
            'group_count': 1,
            'class_count': 1,
        })


@override_settings(AWS_STORAGE_BUCKET_NAME='test-bucket')
class IsicTaxonomyPublisherTest(TestCase):
    def setUp(self):
        IsicTaxonomyConfig.objects.all().delete()

    @patch('api.isic_taxonomy.publisher.get_s3_client')
    def test_publish_taxonomy_updates_config_on_success(
        self,
        mock_get_s3_client,
    ):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.list_objects_v2.return_value = {'Contents': []}

        config = IsicTaxonomyConfig.load()
        config.version = 1
        config.save()

        result = publish_taxonomy(
            file_content=SAMPLE_CSV,
            filename='sample.csv',
        )

        self.assertEqual(result['version'], 2)
        self.assertEqual(
            result['json_s3_key'],
            'taxonomy/isic4/v2/isic_rev4.json',
        )
        self.assertEqual(
            result['bundle_s3_key'],
            'taxonomy/isic4/v2/isicRev4Taxonomy.js',
        )

        config.refresh_from_db()
        self.assertEqual(config.version, 2)
        self.assertTrue(config.is_active)
        self.assertEqual(config.class_count, 1)
        self.assertEqual(config.last_error, '')

        self.assertEqual(s3_client.put_object.call_count, 3)
        self.assertEqual(s3_client.copy_object.call_count, 3)

    @patch('api.isic_taxonomy.publisher.get_s3_client')
    def test_publish_taxonomy_rolls_back_on_upload_failure(
        self,
        mock_get_s3_client,
    ):
        s3_client = MagicMock()
        mock_get_s3_client.return_value = s3_client
        s3_client.put_object.side_effect = Exception('S3 unavailable')
        s3_client.list_objects_v2.return_value = {'Contents': []}

        config = IsicTaxonomyConfig.load()
        config.version = 3
        config.is_active = True
        config.json_s3_key = 'taxonomy/isic4/v3/isic_rev4.json'
        config.bundle_s3_key = 'taxonomy/isic4/v3/isicRev4Taxonomy.js'
        config.class_count = 1
        config.save()

        with self.assertRaises(IsicTaxonomyPublishError):
            publish_taxonomy(
                file_content=SAMPLE_CSV,
                filename='sample.csv',
            )

        config.refresh_from_db()
        self.assertEqual(config.version, 3)
        self.assertEqual(
            config.json_s3_key,
            'taxonomy/isic4/v3/isic_rev4.json',
        )
        self.assertIn('S3 unavailable', config.last_error)
