"""Shared fixtures for the ``contribot`` unit tests.

The tests exercise :class:`contribot.ContriBot` without touching a real
database or network. To do that we:

* put the ``source`` directory on ``sys.path`` so the flat imports inside
  ``contribot`` (``from utils import ...`` / ``from known_countries import ...``)
  resolve;
* build a small in-memory error-codes configuration workbook so the diagnosis
  machinery has severities and Jinja templates to render;
* provide a ``make_contribution`` factory that writes a DataFrame to a temporary
  ``.xlsx`` and returns a fully constructed ``ContriBot`` instance.
"""

import os
import sys

import pandas as pd
import pytest

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

import contribot  # noqa: E402


ALLOWED_COLUMNS = [
    "country",
    "name",
    "address",
    "sector_product_type",
    "facility_type_processing_type",
    "number_of_workers",
    "parent_company",
    "lat",
    "lng",
]

# Every code the production code can emit. Anything not overridden below gets
# these defaults so ``_add_diagnosis`` never falls into the "unknown code" path
# unless a test explicitly wants it to.
_ALL_CODES = [f"T{n:04d}" for n in range(1, 17)] + [f"C{n:04d}" for n in range(1, 27)]

# code -> overrides for the config row
_CODE_OVERRIDES = {
    # Table-level critical findings.
    "T0001": {"severity": 100, "error": "missing country column"},
    "T0002": {"severity": 100, "error": "missing name column"},
    "T0003": {"severity": 100, "error": "missing address column"},
    "T0004": {"severity": 100, "error": "missing sector_product_type column"},
    "T0005": {"severity": 100, "error": "lat without lng"},
    "T0006": {"severity": 100, "error": "lng without lat"},
    "T0007": {"severity": 50, "error": "both lat and lng present"},
    "T0008": {"severity": 0, "error": "unrecognised column {{column}}"},
    "T0009": {"severity": 100, "error": "empty table"},
    "T0015": {"severity": 0, "error": "extra sheets: {{existing_sheets}}"},
    "T0016": {"severity": 5, "error": "too many lines: {{num_lines}}"},
    # Duplicate findings.
    "T0010": {"severity": 100, "error": "identical rows {{row_1}} {{row_2}}"},
    "T0011": {"severity": 50, "error": "very similar rows {{row_1}} {{row_2}}"},
    "T0012": {"severity": 20, "error": "similar rows {{row_1}} {{row_2}}"},
    "T0013": {"severity": 50, "error": "different unit {{row_1}} {{row_2}}"},
    "T0014": {"severity": 50, "error": "numeric diff {{row_1}} {{row_2}}"},
    # Column-level findings.
    "C0001": {"severity": 100, "style_findings": "Bad",
              "error": "country '{{country}}' is not recognised"},
    "C0002": {"severity": 100, "error": "no country column"},
    "C0003": {"severity": 20, "error": "hong kong in address"},
    "C0004": {"severity": 20, "error": "macao in address"},
    "C0005": {"severity": 20, "error": "taiwan in address"},
    "C0006": {"severity": 30, "error": "country {{country_in_address}} in address, "
                                       "country column says {{country}}"},
    "C0007": {"severity": 10, "style_findings": "",
              "error": "unusual characters {{unusual_characters}} in {{column}}"},
    "C0008": {"severity": 50, "auto_fix": True, "style_fixed": "Good",
              "error": "double quotes present",
              "fixes_comment": "removed double quotes"},
    "C0009": {"severity": 50, "auto_fix": True, "style_fixed": "Good",
              "error": "PO box in address", "fixes_comment": "removed po box"},
    "C0010": {"severity": 5, "auto_fix": True, "style_fixed": "Good",
              "error": "leading blank", "fixes_comment": "trimmed"},
    "C0011": {"severity": 30, "auto_fix": True, "style_fixed": "Bad",
              "error": "trailing blank", "fixes_comment": "trimmed"},
    "C0012": {"severity": 7, "auto_fix": True, "style_fixed": "Neutral",
              "error": "double space", "fixes_comment": "collapsed"},
    "C0013": {"severity": 8, "auto_fix": True, "error": "tab character"},
    "C0014": {"severity": 9, "auto_fix": True, "error": "carriage return"},
    "C0015": {"severity": 10, "auto_fix": True, "style_fixed": "Neutral",
              "error": "newline"},
    "C0016": {"severity": 50, "error": "value length {{cell_len}} exceeds limit"},
    "C0017": {"severity": 20, "error": "name too short: {{name_len}}"},
    "C0018": {"severity": 20, "error": "address too short: {{address_len}}"},
    "C0019": {"severity": 30, "style_fixed": "Good",
              "error": "excel error token {{invalid_token}}"},
    "C0020": {"severity": 15, "auto_fix": True, "style_fixed": "Neutral",
              "error": "{{num_consecutive_commas}} consecutive commas",
              "fixes_comment": "collapsed commas"},
    "C0021": {"severity": 15, "auto_fix": True, "error": "comma inside pipe field"},
    "C0022": {"severity": 15, "auto_fix": True,
              "error": "{{num_commas}} commas in {{column}}",
              "fixes_comment": "removed commas"},
    "C0023": {"severity": 15, "auto_fix": True,
              "error": "{{num_commas}} commas, {{num_fields}} fields",
              "fixes_comment": "commas to pipes"},
    "C0024": {"severity": 5, "error": "field too long"},
    "C0025": {"severity": 5, "error": "short country code {{country_in_address}} "
                                      "in address vs {{country}}"},
    "C0026": {"severity": 5, "error": "empty column {{column}}"},
}


def _build_config_frame():
    rows = []
    for code in _ALL_CODES:
        row = {
            "code": code,
            "level": "table" if code.startswith("T") else "column",
            "severity": 1,
            "style_findings": "",
            "style_fixed": "",
            "auto_fix": False,
            "topic": "test",
            "error": f"default error for {code}",
            "corrective_action": f"fix {code}",
            "fixes_comment": "",
        }
        row.update(_CODE_OVERRIDES.get(code, {}))
        rows.append(row)
    return pd.DataFrame(rows)


@pytest.fixture(scope="session")
def config_path(tmp_path_factory):
    """Write the error-codes workbook once per test session."""
    path = tmp_path_factory.mktemp("config") / "0000.error_codes.xlsx"
    _build_config_frame().to_excel(path, sheet_name="Definitions", index=False)
    return str(path)


def _default_frame():
    return pd.DataFrame(
        {
            "country": ["Bangladesh", "Germany"],
            "name": ["Acme Textiles Limited", "Globex Manufacturing GmbH"],
            "address": [
                "123 Industrial Road, Dhaka Division",
                "45 Fabrikstrasse, Berlin Region Area",
            ],
            "sector_product_type": ["Apparel|Textiles", "Electronics|Components"],
        }
    )


@pytest.fixture
def make_contribution(tmp_path, config_path, monkeypatch):
    """Factory returning a constructed ``ContriBot``.

    ``df`` defaults to a small valid two-row frame. Pass ``with_config=False`` to
    build an instance whose config lookup finds nothing (the empty-config path).
    All relative file writes are contained to ``tmp_path`` via chdir.
    """
    monkeypatch.chdir(tmp_path)
    created = {}

    def _make(df=None, with_config=True, filename="contribution.xlsx"):
        if df is None:
            df = _default_frame()
        source_path = tmp_path / filename
        df.to_excel(source_path, index=False)
        cfg = config_path if with_config else str(tmp_path / "does-not-exist.xlsx")
        instance = contribot.ContriBot(str(source_path), config_file=cfg)
        created["last"] = instance
        return instance

    return _make


@pytest.fixture
def contribution(make_contribution):
    """A ready-to-use instance built from the default frame."""
    return make_contribution()
