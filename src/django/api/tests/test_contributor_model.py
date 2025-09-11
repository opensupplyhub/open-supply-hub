import uuid
import pytest

from unittest.mock import patch

# NOTE: Testing stack detected: pytest + pytest-django.
# If using Django's TestCase, tests should still run under pytest-django with the db fixture.

pytestmark = pytest.mark.django_db

# Import the model from its canonical location.
# Adjust import if your app label differs.
try:
    from api.models import Contributor  # common pattern if models are exposed via api/models/__init__.py
except Exception:
    # Fallback to direct path often used in monorepos
    from api.tests.test_contributor_model import Contributor  # noqa: F401,E402


@pytest.mark.describe("Contributor.__str__")
def test_contributor_str_does_not_crash(django_user_model):
    # Create minimal User required by OneToOneField
    admin = django_user_model.objects.create(username="admin_user")
    try:
        # Create a minimal Contributor; many optional fields can be blank
        # We import Contributor lazily inside test to support either import path
        try:
            from api.models import Contributor
        except Exception:
            from api.tests.test_contributor_model import Contributor
        c = Contributor.objects.create(
            admin=admin,
            name="Acme Corp",
            description="",
            website="",
            contrib_type="Brand / Retailer",
            other_contrib_type=None,
            is_verified=False,
            verification_notes="",
        )
        s = str(c)
        assert "Acme Corp" in s
        assert f"({c.id})" in s
    finally:
        admin.delete()


@pytest.mark.describe("Contributor.uuid")
def test_contributor_uuid_auto_generated_and_unique(django_user_model):
    admin1 = django_user_model.objects.create(username="user1")
    admin2 = django_user_model.objects.create(username="user2")
    try:
        try:
            from api.models import Contributor
        except Exception:
            from api.tests.test_contributor_model import Contributor
        c1 = Contributor.objects.create(
            admin=admin1,
            name="One",
            description="",
            website="",
            contrib_type="Brand / Retailer",
        )
        c2 = Contributor.objects.create(
            admin=admin2,
            name="Two",
            description="",
            website="",
            contrib_type="Brand / Retailer",
        )
        assert isinstance(c1.uuid, uuid.UUID)
        assert isinstance(c2.uuid, uuid.UUID)
        assert c1.uuid != c2.uuid
    finally:
        admin1.delete()
        admin2.delete()


@pytest.mark.describe("Contributor.prefix_with_count pluralization and special cases")
class TestPrefixWithCount:
    def _get_model(self):
        try:
            from api.models import Contributor
        except Exception:
            from api.tests.test_contributor_model import Contributor
        return Contributor

    @pytest.mark.parametrize(
        "value,count,expected",
        [
            ("Brand / Retailer", 2, "2 Brands / Retailers"),
            ("Union", 5, "5 Unions"),
            (
                "Facility / Factory / Manufacturing Group / Supplier / Vendor",
                3,
                "3 Facilities / Factories / Manufacturing Groups / Suppliers / Vendors",
            ),
        ],
    )
    def test_count_not_one_uses_plural_mapping_when_available(self, value, count, expected):
        Contributor = self._get_model()
        assert Contributor.prefix_with_count(value, count) == expected

    def test_count_not_one_without_mapping_falls_back_to_raw_value(self):
        Contributor = self._get_model()
        assert Contributor.prefix_with_count("Unknown Type", 7) == "7 Unknown Type"

    @pytest.mark.parametrize("variant", ["Other", "other", "OTHER", "oThEr"])
    def test_count_one_other_is_one_Other_not_an_other(self, variant):
        Contributor = self._get_model()
        result = Contributor.prefix_with_count(variant, 1)
        # Expect exact "One <input variant>"
        assert result == f"One {variant}"

    def test_count_one_delegates_to_prefix_a_an(self, monkeypatch):
        Contributor = self._get_model()

        # We patch the imported name in the module where it's used.
        # Attempt patching both candidate module paths for robustness.
        called = {"count": 0}

        def _fake_prefix(val):
            called["count"] += 1
            assert val == "Academic / Researcher / Journalist / Student"
            return "An Academic / Researcher / Journalist / Student"

        try:
            import api.models as maybe_models
            monkeypatch.setattr(maybe_models, "prefix_a_an", _fake_prefix, raising=False)
        except Exception:
            import api.tests.test_contributor_model as maybe_local
            monkeypatch.setattr(maybe_local, "prefix_a_an", _fake_prefix, raising=False)

        res = Contributor.prefix_with_count("Academic / Researcher / Journalist / Student", 1)
        assert res == "An Academic / Researcher / Journalist / Student"
        assert called["count"] == 1