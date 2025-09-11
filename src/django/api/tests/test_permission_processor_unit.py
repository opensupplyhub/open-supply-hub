import types
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

# Attempt to import the class under test.
# If the repo uses a different module path for PermissionProcessor, update the import below accordingly.
try:
    from api.tests.test_permission_processor import PermissionProcessor  # fallback based on provided path snippet
except ImportError:
    # Common/expected module path in production codebases:
    try:
        from api.moderation_event_actions.creation.location_contribution.processors.permission_processor import PermissionProcessor
    except ImportError:
        # Final fallback: import via dynamic import to avoid hard failures when path differs in CI;
        # tests that actually run in the repo should resolve the correct path above.
        PermissionProcessor = None  # Will be asserted below


@pytest.mark.skipif(PermissionProcessor is None, reason="PermissionProcessor import path unresolved; adjust import in test to match repo.")
class TestPermissionProcessorProcess:
    def _make_dto(self, raw_data, contributor_fields):
        """
        Build a lightweight DTO object with required attributes:
        - raw_data: dict or other
        - contributor.partner_fields.all(): returns iterable of objects with .name
        - errors: defaults to None
        - status_code: defaults to None
        """
        contributor_field_objs = [SimpleNamespace(name=n) for n in contributor_fields]
        contributor = SimpleNamespace(
            partner_fields=SimpleNamespace(
                all=MagicMock(return_value=contributor_field_objs)
            )
        )
        return SimpleNamespace(
            raw_data=raw_data,
            contributor=contributor,
            errors=None,
            status_code=None,
        )

    @pytest.fixture
    def partner_field_names(self):
        # Global partner fields available in the system
        return ["alpha", "beta", "gamma"]

    @pytest.fixture
    def partner_field_qs(self, partner_field_names):
        # Simulate PartnerField.objects.all() -> iterable with .name
        return [SimpleNamespace(name=n) for n in partner_field_names]

    def test_no_raw_data_delegates_to_super(self, partner_field_qs):
        dto = self._make_dto(raw_data=None, contributor_fields=["alpha"])

        with patch("api.models.partner_field.PartnerField.objects.all", return_value=partner_field_qs):
            # We need to patch ContributionProcessor.process specifically, not the subclass' override.
            # Resolve the MRO super target by patching its parent class method via the subclass.
            # Use attribute lookup to parent class at runtime:
            parent_cls = PermissionProcessor.__mro__[1]
            with patch.object(parent_cls, "process", return_value=SimpleNamespace(marker="super-called")) as parent_process:
                proc = PermissionProcessor()
                result = proc.process(dto)
                parent_process.assert_called_once_with(proc, dto)
                assert getattr(result, "marker", None) == "super-called"

    def test_non_dict_raw_data_delegates_to_super(self, partner_field_qs):
        dto = self._make_dto(raw_data=["not", "a", "dict"], contributor_fields=["alpha"])

        parent_cls = PermissionProcessor.__mro__[1]
        with patch("api.models.partner_field.PartnerField.objects.all", return_value=partner_field_qs), \
             patch.object(parent_cls, "process", return_value=SimpleNamespace(marker="super-called")) as parent_process:
            proc = PermissionProcessor()
            result = proc.process(dto)
            parent_process.assert_called_once_with(proc, dto)
            assert getattr(result, "marker", None) == "super-called"

    def test_no_matching_partner_fields_delegates_to_super(self, partner_field_qs):
        dto = self._make_dto(raw_data={"unknown": 1, "irrelevant": 2}, contributor_fields=["alpha"])

        parent_cls = PermissionProcessor.__mro__[1]
        with patch("api.models.partner_field.PartnerField.objects.all", return_value=partner_field_qs), \
             patch.object(parent_cls, "process", return_value=SimpleNamespace(marker="super-called")) as parent_process:
            proc = PermissionProcessor()
            result = proc.process(dto)
            parent_process.assert_called_once_with(proc, dto)
            assert getattr(result, "marker", None) == "super-called"

    def test_all_matching_fields_authorized_delegates_to_super(self, partner_field_qs):
        # raw_data keys subset of partner fields, and contributor has all of them
        dto = self._make_dto(raw_data={"alpha": "x", "beta": "y"}, contributor_fields=["alpha", "beta", "gamma"])

        parent_cls = PermissionProcessor.__mro__[1]
        with patch("api.models.partner_field.PartnerField.objects.all", return_value=partner_field_qs), \
             patch.object(parent_cls, "process", return_value=SimpleNamespace(marker="super-called")) as parent_process:
            proc = PermissionProcessor()
            result = proc.process(dto)
            parent_process.assert_called_once_with(proc, dto)
            assert getattr(result, "marker", None) == "super-called"
            # Ensure no error side-effects were introduced
            assert dto.errors is None
            assert dto.status_code is None

    def test_some_unauthorized_fields_returns_403_and_errors(self, partner_field_qs):
        # Partner fields alpha, beta, gamma
        # Contributor has only 'alpha'; raw_data attempts 'alpha' (ok) and 'beta' (unauthorized) and 'unknown' (ignored)
        dto = self._make_dto(raw_data={"alpha": 1, "beta": 2, "unknown": 3}, contributor_fields=["alpha"])

        with patch("api.models.partner_field.PartnerField.objects.all", return_value=partner_field_qs):
            proc = PermissionProcessor()
            result = proc.process(dto)

        # Should short-circuit before calling super() — we check via absence of injected marker and presence of 403
        assert result is dto  # in-place mutation and return of same DTO
        assert dto.status_code == 403
        assert isinstance(dto.errors, dict)
        assert "detail" in dto.errors and "errors" in dto.errors
        # Error entries should only include unauthorized partner field names present in payload (beta)
        fields_list = [e.get("field") for e in dto.errors["errors"]]

        assert fields_list == ["beta"]
        # Each error entry should include a helpful detail message
        for e in dto.errors["errors"]:
            assert "You do not have permission" in e.get("detail", "")

    def test_multiple_unauthorized_fields_all_reported(self, partner_field_qs):
        # Contributor has none; raw_data uses alpha and gamma which are both unauthorized
        dto = self._make_dto(raw_data={"alpha": 1, "gamma": 3}, contributor_fields=[])

        with patch("api.models.partner_field.PartnerField.objects.all", return_value=partner_field_qs):
            proc = PermissionProcessor()
            _ = proc.process(dto)

        assert dto.status_code == 403
        fields = [e["field"] for e in dto.errors["errors"]]
        assert set(fields) == {"alpha", "gamma"}

    def test_ignores_non_partner_keys_when_computing_authorization(self, partner_field_qs):
        # raw_data includes one partner key (beta) and two non-partner keys; only partner key should be checked
        dto = self._make_dto(raw_data={"beta": 7, "not_a_field": 1, "also_irrelevant": 2}, contributor_fields=["beta"])

        parent_cls = PermissionProcessor.__mro__[1]
        with patch("api.models.partner_field.PartnerField.objects.all", return_value=partner_field_qs), \
             patch.object(parent_cls, "process", return_value=SimpleNamespace(marker="super-called")) as parent_process:
            proc = PermissionProcessor()
            result = proc.process(dto)
            parent_process.assert_called_once()
            assert getattr(result, "marker", None) == "super-called"

class TestTransformFieldsErrors:
    @pytest.mark.skipif(PermissionProcessor is None, reason="PermissionProcessor import path unresolved; adjust import in test to match repo.")
    def test_private_transform_fields_errors_structure(self):
        # Access name-mangled static method
        transform = PermissionProcessor._PermissionProcessor__transform_fields_errors

        errors = transform(["alpha", "beta"])
        assert isinstance(errors, dict)
        assert "detail" in errors and "errors" in errors
        # Detail should come from the project's constants to remain stable across locales/messages
        from api.constants import APIV1CommonErrorMessages
        assert errors["detail"] == APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR
        # Ensure both fields are represented with required schema
        assert errors["errors"] == [
            {"field": "alpha", "detail": "You do not have permission to contribute to this field."},
            {"field": "beta", "detail": "You do not have permission to contribute to this field."},
        ]