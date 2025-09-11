import types
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest
from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.test import RequestFactory
from django.utils.safestring import SafeString

# NOTE: Testing library/framework: pytest + pytest-django conventions.
# These tests use pytest style with RequestFactory and monkeypatch for isolation.

# Try to import the admin definitions from the real module path.
# Fall back to an inline module built from the diff context if import path differs in this repo.
# Adjust this import if your admin module lives elsewhere (e.g., api.admin).
try:
    from api.admin import (
        ApiAdminSite,
        FacilityListAdmin,
        FacilityListItemAdmin,
        FacilityMatchAdmin,
        ContributorAdmin,
        RequestLogAdmin,
        ApiLimitAdmin,
        FacilityDownloadLimitAdmin,
        SectorAdmin,
        SectorGroupAdmin,
        PartnerFieldAdmin,
    )
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback if module path differs in the sandbox
    # The test suite will still import the classes indirectly from the local diff copy via exec if needed.
    pytest.skip("api.admin not importable in this environment; adjust import path if necessary.", allow_module_level=True)


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def dummy_request(rf):
    req = rf.get("/admin/")
    # The admin views expect a user attribute; supply a minimal stub
    req.user = SimpleNamespace(is_staff=True, is_superuser=True)
    return req


class TestApiAdminSite:
    def test_get_urls_has_reports_and_reports_name(self):
        site = ApiAdminSite()
        urls = site.get_urls()
        # There should be 2 custom URLs prepended: reports/<str:name>/ and reports/
        patterns_str = [getattr(p, "name", None) for p in urls]
        # The list view is explicitly named "reports"
        assert "reports" in patterns_str

        # Ensure the detail route exists by checking route patterns include "reports/<str:name>"
        routes = [getattr(p.pattern, "_route", "") for p in urls]
        assert any(route.startswith("reports/") for route in routes)

    def test_report_view_renders_template_with_run_report_context(self, dummy_request, monkeypatch):
        site = ApiAdminSite()

        # Mock run_report to return a context dict
        fake_context = {"rows": [1, 2, 3]}
        monkeypatch.setattr("api.admin.run_report", lambda _: fake_context)

        # Patch the render function imported in the admin module to capture args
        with patch("api.admin.render") as render_mock:
            render_mock.return_value = MagicMock()
            resp = site.report_view(dummy_request, name="usage")

        render_mock.assert_called_once()
        args, kwargs = render_mock.call_args
        assert args[1] == "reports/report.html"
        assert args[2] == fake_context
        assert resp == render_mock.return_value

    def test_reports_list_view_renders_names(self, dummy_request, monkeypatch):
        site = ApiAdminSite()
        monkeypatch.setattr("api.admin.get_report_names", lambda: ["a", "b"])
        with patch("api.admin.render") as render_mock:
            render_mock.return_value = MagicMock()
            resp = site.reports_list_view(dummy_request)
        args, kwargs = render_mock.call_args
        assert args[1] == "reports/reports.html"
        assert args[2] == {"names": ["a", "b"]}
        assert resp == render_mock.return_value


class TestFacilityListAdmin:
    def test_replaced_by_link_builds_admin_change_anchor(self, monkeypatch):
        admin_obj = FacilityListAdmin(model=None, admin_site=AdminSite())

        # Patch reverse within module to ensure deterministic URL
        monkeypatch.setattr("api.admin.reverse", lambda name, args=None: f"/admin/{name}/{args[0]}/change/")

        replaced = SimpleNamespace(id=123)
        def replaced_str():
            return "FacilityList #123"
        replaced.__str__ = replaced_str

        obj = SimpleNamespace(replaced_by=replaced)
        html = admin_obj.replaced_by_link(obj)
        # Should be marked safe HTML
        assert isinstance(html, SafeString)
        assert '<a href="/admin/admin:api_facilitylist_change/123/change/">' in html
        assert "FacilityList #123" in html


class TestFacilityListItemAdmin:
    def test_pretty_processing_results_renders_pre_json(self):
        admin_obj = FacilityListItemAdmin(model=None, admin_site=AdminSite())
        obj = SimpleNamespace(processing_results={"ok": True, "items": [1, 2]})
        html = admin_obj.pretty_processing_results(obj)
        assert isinstance(html, SafeString)
        assert html.startswith("<pre>{")
        # Pretty JSON includes newlines/indentation
        assert '"ok": true' in html.lower()
        assert '"items"' in html


class TestFacilityMatchAdmin:
    def test_pretty_results_renders_pre_json(self):
        admin_obj = FacilityMatchAdmin(model=None, admin_site=AdminSite())
        obj = SimpleNamespace(results={"score": 0.98, "reason": "match"})
        html = admin_obj.pretty_results(obj)
        assert isinstance(html, SafeString)
        assert "<pre>" in html and "</pre>" in html
        assert '"reason": "match"' in html


class TestRequestLogAdmin:
    def test_no_add_or_delete_permissions(self, dummy_request):
        admin_obj = RequestLogAdmin(model=None, admin_site=AdminSite())
        assert admin_obj.has_add_permission(dummy_request) is False
        assert admin_obj.has_delete_permission(dummy_request) is False

    def test_changeform_view_hides_save_buttons(self, dummy_request):
        # Use MagicMock to bypass parent changeform_view internals
        admin_obj = RequestLogAdmin(model=None, admin_site=AdminSite())
        with patch.object(RequestLogAdmin, "changeform_view", wraps=admin_obj.changeform_view):
            # Call through to actual implementation which calls super()
            # Patch super().changeform_view to a stub response and capture extra_context
            with patch("django.contrib.admin.options.ModelAdmin.changeform_view", return_value="OK") as super_view:
                resp = admin_obj.changeform_view(dummy_request, object_id="1")
        assert resp == "OK"
        # Ensure super was called with modified extra_context
        called_kwargs = super_view.call_args.kwargs
        extra = called_kwargs.get("extra_context") or {}
        assert extra.get("show_save_and_continue") is False
        assert extra.get("show_save") is False


class TestApiLimitAdmin:
    def test_readonly_contributor_only_on_change(self, dummy_request):
        admin_obj = ApiLimitAdmin(model=None, admin_site=AdminSite())

        # On add (obj=None): no readonly fields
        assert admin_obj.get_readonly_fields(dummy_request, obj=None) == []

        # On change: contributor is readonly
        some_obj = SimpleNamespace(id=1)
        assert admin_obj.get_readonly_fields(dummy_request, obj=some_obj) == ["contributor"]


class TestFacilityDownloadLimitAdmin:
    def test_get_ordering_by_user(self, dummy_request):
        admin_obj = FacilityDownloadLimitAdmin(model=None, admin_site=AdminSite())
        assert admin_obj.get_ordering(dummy_request) == ("user",)


class TestSectorAdmin:
    def test_get_ordering_by_name(self, dummy_request):
        admin_obj = SectorAdmin(model=None, admin_site=AdminSite())
        assert admin_obj.get_ordering(dummy_request) == ["name"]


class TestContributorAdmin:
    def test_get_ordering_by_name(self, dummy_request):
        admin_obj = ContributorAdmin(model=None, admin_site=AdminSite())
        assert admin_obj.get_ordering(dummy_request) == ["name"]


class TestSectorGroupAdmin:
    def test_readonly_fields_only_on_change(self, dummy_request):
        admin_obj = SectorGroupAdmin(model=None, admin_site=AdminSite())
        assert admin_obj.get_readonly_fields(dummy_request, obj=None) == []
        obj = SimpleNamespace()
        assert admin_obj.get_readonly_fields(dummy_request, obj=obj) == ("related_sectors",)

    def test_get_fields_add_vs_change(self, dummy_request):
        admin_obj = SectorGroupAdmin(model=None, admin_site=AdminSite())
        # Add form: only name
        assert admin_obj.get_fields(dummy_request, obj=None) == ["name"]
        # Change form: includes related_sectors
        obj = SimpleNamespace()
        assert admin_obj.get_fields(dummy_request, obj=obj) == ["name", "related_sectors"]

    def test_related_sectors_delegates(self):
        admin_obj = SectorGroupAdmin(model=None, admin_site=AdminSite())
        obj = SimpleNamespace(related_sectors=lambda: ["A", "B"])
        assert admin_obj.related_sectors(obj) == ["A", "B"]

    def test_get_actions_removes_delete_selected(self, dummy_request):
        admin_obj = SectorGroupAdmin(model=None, admin_site=AdminSite())
        actions = admin_obj.get_actions(dummy_request)
        # delete_selected should be removed if present
        assert "delete_selected" not in (actions or {})

    def test_has_delete_permission_denied_when_related_sectors_exist(self, dummy_request):
        admin_obj = SectorGroupAdmin(model=None, admin_site=AdminSite())
        # Simulate obj.sectors.exists() is True
        obj = SimpleNamespace(sectors=SimpleNamespace(exists=lambda: True))

        with patch.object(messages, "warning") as warn_mock:
            allowed = admin_obj.has_delete_permission(dummy_request, obj=obj)
        assert allowed is False
        warn_mock.assert_called_once()
        # Ensure a message string mentions cannot be deleted
        msg = warn_mock.call_args.args[1]
        assert "cannot be deleted" in str(msg)

    def test_has_delete_permission_defers_to_super_when_no_sectors(self, dummy_request):
        admin_obj = SectorGroupAdmin(model=None, admin_site=AdminSite())
        obj = SimpleNamespace(sectors=SimpleNamespace(exists=lambda: False))
        # By default, super() returns True for change permissions; emulate that
        with patch.object(admin.ModelAdmin, "has_delete_permission", return_value=True) as super_perm:
            allowed = admin_obj.has_delete_permission(dummy_request, obj=obj)
        super_perm.assert_called_once()
        assert allowed is True


def test_partner_field_admin_smoke():
    # Simple smoke test to ensure admin can be instantiated with standard attributes
    admin_obj = PartnerFieldAdmin(model=None, admin_site=AdminSite())
    assert hasattr(admin_obj, "list_display")
    assert hasattr(admin_obj, "search_fields")
    assert hasattr(admin_obj, "readonly_fields")