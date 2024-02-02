from api.serializers import FacilityCreateBodySerializer

from django.test import TestCase


class FacilityCreateBodySerializerTest(TestCase):
    def test_valid_data(self):
        serializer = FacilityCreateBodySerializer(
            data={
                "sector": "Apparel",
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertTrue(serializer.is_valid())

    def test_missing_fields(self):
        serializer = FacilityCreateBodySerializer(
            data={
                "sector": "Apparel",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertNotIn("sector", serializer.errors)
        self.assertIn("country", serializer.errors)
        self.assertNotIn("name", serializer.errors)
        self.assertNotIn("address", serializer.errors)

        serializer = FacilityCreateBodySerializer(
            data={
                "sector": "Apparel",
                "country": "United States",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertNotIn("sector", serializer.errors)
        self.assertIn("name", serializer.errors)
        self.assertNotIn("country", serializer.errors)
        self.assertNotIn("address", serializer.errors)

        serializer = FacilityCreateBodySerializer(
            data={
                "sector": "Apparel",
                "country": "United States",
                "name": "Pants Hut",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertNotIn("sector", serializer.errors)
        self.assertIn("address", serializer.errors)
        self.assertNotIn("country", serializer.errors)
        self.assertNotIn("name", serializer.errors)

    def test_invalid_country(self):
        serializer = FacilityCreateBodySerializer(
            data={
                "sector": "Apparel",
                "country": "Notrealia",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("country", serializer.errors)

    def test_invalid_sector_type(self):
        serializer = FacilityCreateBodySerializer(
            data={
                "sector": 7,
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("sector", serializer.errors)

        serializer = FacilityCreateBodySerializer(
            data={
                "sector": ["Apparel", 7],
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("sector", serializer.errors)

    def test_invalid_sector_empty(self):
        serializer = FacilityCreateBodySerializer(
            data={
                "sector": [" "],
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("sector", serializer.errors)

        serializer = FacilityCreateBodySerializer(
            data={
                "sector": " ",
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("sector", serializer.errors)

        serializer = FacilityCreateBodySerializer(
            data={
                "sector": [],
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("sector", serializer.errors)

    def test_sector_pipe_split(self):
        serializer = FacilityCreateBodySerializer(
            data={
                "sector": "Apparel|Industry",
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data["sector"], ["Apparel", "Industry"])

    def test_sector_trim(self):
        serializer = FacilityCreateBodySerializer(
            data={
                "sector": "Apparel | Industry",
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data["sector"], ["Apparel", "Industry"])

        serializer = FacilityCreateBodySerializer(
            data={
                "sector": " Apparel|Industry ",
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data["sector"], ["Apparel", "Industry"])

        serializer = FacilityCreateBodySerializer(
            data={
                "sector": [" Apparel ", " Industry "],
                "country": "United States",
                "name": "Pants Hut",
                "address": "123 Main St, Anywhereville, PA",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data["sector"], ["Apparel", "Industry"])
