"""The contributor's list-cleaning review in the report (OSDEV-3398).

Rows the review removed are kept in the file but not reported on; the Cleaning
sheet lists every suggestion with the decision taken; the Summary and the
handler get the two counts moderators ask for.
"""

import copy

import openpyxl
import pandas as pd
import pytest

from lib import contribot


def _frame():
    return pd.DataFrame(
        {
            "country": ["Bangladesh", "Bangladesh", "Germany"],
            "name": [
                "Acme Textiles Limited",
                "Acme Textiles Limited",
                "Globex Manufacturing GmbH",
            ],
            "address": [
                "123 Industrial Road, Dhaka Division",
                "PO Box 12, Dhaka Division",
                "45 Fabrikstrasse, Berlin Region Area",
            ],
            "sector_product_type": ["Apparel", "Apparel", "Electronics"],
            # row 3 (the second data row) was removed in the review
            "os_hub_cleaning": ["", "removed: duplicate of row 2", ""],
        }
    )


def _suggestion(**fields):
    base = {
        "id": 1,
        "row_number": 2,
        "kind": "ISSUE",
        "field": "address",
        "code": "code",
        "source": "",
        "severity": "",
        "original_value": "",
        "corrected_value": "",
        "note": "",
        "extra": {},
        "decision": "PENDING",
        "decided_value": "",
        "decided_at": None,
        "applied": False,
    }
    base.update(fields)
    return base


PAYLOAD = {
    "enabled": True,
    "window_open": False,
    "run": {
        "id": 7,
        "status": "COMPLETE",
        "runner": "stepfunctions",
        "prompt_version": "02",
        "created_at": "2026-11-16T10:00:00Z",
        "submitted_at": "2026-11-16T10:12:30Z",
        "applied_at": "2026-11-16T10:12:30Z",
        "closed_reason": "submitted",
    },
    "summary": {
        "rows_total": 3,
        "rows_flagged_unresolved": 1,
        "corrections_rejected": 1,
    },
    "breakdown": {
        "auto_applied": 1,
        "auto_turned_off": 0,
        "fixes_offered": 1,
        "fixes_accepted": 0,
        "fixes_kept_original": 1,
        "values_typed": 0,
        "rows_removed_by_review": 1,
        "flags_offered": 1,
        "flags_resolved": 0,
        "flags_left_as_uploaded": 1,
    },
    "rows": [
        {
            "row_number": 4,
            "suggestions": [
                _suggestion(
                    row_number=4,
                    kind="CORRECTION",
                    code="country_in_address",
                    source="rules",
                    original_value="45 Fabrikstrasse, Berlin Region Area, Germany",
                    corrected_value="45 Fabrikstrasse, Berlin Region Area",
                    note="The country name was removed from the address.",
                    decision="REJECTED",
                ),
            ],
        },
        {
            "row_number": 2,
            "suggestions": [
                _suggestion(
                    row_number=2,
                    code="address_too_few",
                    severity="internal_note",
                    original_value="123 Industrial Road, Dhaka Division",
                    note="For the moderator \x01only.",
                ),
                _suggestion(
                    row_number=2,
                    kind="CORRECTION",
                    field="country",
                    code="country_code",
                    source="rules",
                    original_value="Bangladesh",
                    corrected_value="BD",
                    decision="ACCEPTED",
                    extra={"auto": True},
                    applied=True,
                ),
            ],
        },
        {
            "row_number": 3,
            "suggestions": [
                _suggestion(
                    row_number=3,
                    code="address_po_box",
                    severity="must_fix",
                    source="model",
                    original_value="PO Box 12, Dhaka Division",
                    note="The address is a PO box.",
                    decision="REJECTED",
                ),
                _suggestion(
                    row_number=3,
                    kind="REMOVAL",
                    field="row",
                    code="duplicate",
                    decision="ACCEPTED",
                    extra={"auto": True, "duplicate_of": 2},
                    applied=True,
                ),
            ],
        },
    ],
}


def _cleaning_table(ws):
    """The suggestion table of a Cleaning sheet as a list of dicts."""
    header_row = next(r for r in range(1, ws.max_row + 1) if ws[f"A{r}"].value == "Row")
    names = [ws.cell(row=header_row, column=c).value for c in range(1, 13)]
    rows = []
    for r in range(header_row + 1, ws.max_row + 1):
        values = [ws.cell(row=r, column=c).value for c in range(1, 13)]
        if values[0] is None:
            break
        rows.append(dict(zip(names, values)))
    return rows


def _header(ws):
    out = {}
    for r in range(1, ws.max_row + 1):
        label = ws[f"A{r}"].value
        if label == "Row":
            break
        if label:
            out[label] = ws[f"B{r}"].value
    return out


class TestRemovedRows:
    def test_removed_rows_come_from_the_tag_column(self, make_contribution):
        osh = make_contribution(df=_frame())
        assert osh.removed_rows == {3}

    def test_no_tag_column_means_nothing_removed(self, contribution):
        assert contribution.removed_rows == set()

    def test_not_read_rows_are_still_checked(self, make_contribution):
        df = _frame()
        df.loc[1, "os_hub_cleaning"] = "not read: fix the row and re-upload"
        osh = make_contribution(df=df)
        assert osh.removed_rows == set()

    def test_tag_column_is_not_an_unrecognised_column(self, make_contribution):
        osh = make_contribution(df=_frame())
        osh.check_table()
        assert not any(d["code"] == "T0008" for d in osh.diagnostics_table)
        metrics = {(s["metric"], s["value"]) for s in osh.statistics}
        assert ("num_rows", 3) in metrics
        assert ("num_rows_removed_in_review", 1) in metrics

    def test_findings_on_removed_rows_are_dropped(self, make_contribution):
        osh = make_contribution(df=_frame())
        osh.process()
        po_box = [d for d in osh.diagnostics_column if d["code"] == "C0009"]
        assert po_box == []

    def test_findings_on_kept_rows_stay(self, make_contribution):
        df = _frame()
        df.loc[0, "address"] = "PO Box 9, Dhaka Division"
        osh = make_contribution(df=df)
        osh.process()
        rows = [d["row"] for d in osh.diagnostics_column if d["code"] == "C0009"]
        assert rows == [2]

    @pytest.mark.parametrize(
        "row,kwparams,expected",
        [
            (3, {}, True),
            (2, {}, False),
            ("2 3", {}, True),
            ("", {"row_1": 2, "row_2": 3}, True),
            ("", {"row_1": 2, "row_2": 4}, False),
            ("", {"column": "address"}, False),
        ],
    )
    def test_on_removed_row(self, make_contribution, row, kwparams, expected):
        osh = make_contribution(df=_frame())
        assert osh._on_removed_row(row, kwparams) is expected

    def test_summary_counts_only_kept_rows(self, make_contribution, tmp_path):
        df = _frame()
        df.loc[0, "address"] = "PO Box 9, Dhaka Division"
        osh = make_contribution(df=df)
        osh.process()
        summary = osh.save(targetfolder=str(tmp_path / "out"))
        assert summary["num_lines"] == 2
        assert "cleaning" not in summary

    def test_removed_rows_keep_their_uploaded_values_on_the_fixes_sheet(
        self, make_contribution, tmp_path
    ):
        df = _frame()
        # double quotes are auto-fixed (C0008) on the Fixes sheet as the
        # checks go; the removed row must come out as uploaded, unstyled
        df.loc[0, "name"] = 'Acme "Textiles" Limited'
        df.loc[1, "name"] = 'Acme "Textiles" Limited'
        osh = make_contribution(df=df)
        osh.process()
        osh.save(targetfolder=str(tmp_path / "out"))
        wb = openpyxl.load_workbook(tmp_path / "out" / osh.targetfilename)
        fixes = wb[osh.fixessheet]
        assert fixes["B2"].value == "Acme Textiles Limited"
        assert fixes["B2"].style == "Good"
        assert fixes["B3"].value == 'Acme "Textiles" Limited'
        assert fixes["B3"].style == "Normal"
        assert fixes["B3"].font.strike is True
        assert fixes["B3"].comment is None

    def test_removed_rows_are_struck_through(self, make_contribution, tmp_path):
        osh = make_contribution(df=_frame())
        osh.process()
        osh.save(targetfolder=str(tmp_path / "out"))
        wb = openpyxl.load_workbook(tmp_path / "out" / osh.targetfilename)
        for sheet in (osh.sourcesheet, "Findings", osh.fixessheet):
            assert wb[sheet]["B3"].font.strike is True
            assert wb[sheet]["B2"].font.strike is not True


class TestCleaningSheet:
    def _saved(self, make_contribution, tmp_path, payload=PAYLOAD, df=None):
        osh = make_contribution(df=_frame() if df is None else df)
        osh.attach_cleaning(copy.deepcopy(payload))
        osh.process()
        summary = osh.save(targetfolder=str(tmp_path / "out"))
        wb = openpyxl.load_workbook(tmp_path / "out" / osh.targetfilename)
        return osh, summary, wb

    def test_no_sheet_without_a_run(self, make_contribution, tmp_path):
        osh = make_contribution(df=_frame())
        osh.process()
        osh.save(targetfolder=str(tmp_path / "out"))
        wb = openpyxl.load_workbook(tmp_path / "out" / osh.targetfilename)
        assert "Cleaning" not in wb.sheetnames

    def test_sheet_sits_after_summary(self, make_contribution, tmp_path):
        _, _, wb = self._saved(make_contribution, tmp_path)
        assert wb.sheetnames[:3] == ["Summary", "Cleaning", "Findings"]

    def test_header_describes_the_run(self, make_contribution, tmp_path):
        _, _, wb = self._saved(make_contribution, tmp_path)
        header = _header(wb["Cleaning"])
        assert header["Cleaning run"] == 7
        assert header["Prompt version"] == "02"
        assert header["Outcome"] == "Submitted by the contributor"
        assert header["Minutes from run to submission"] == 12.5
        assert header["Rows in the list"] == 3
        assert header["Rows removed"] == 1
        assert header["Suggestions"] == 5
        assert header["Must-fix flags unresolved"] == 1
        assert header["Suggested fixes rejected"] == 1
        assert header["Fixes kept as uploaded"] == 1
        assert header["Flags left as uploaded"] == 1

    def test_every_suggestion_is_listed_by_row(self, make_contribution, tmp_path):
        _, _, wb = self._saved(make_contribution, tmp_path)
        table = _cleaning_table(wb["Cleaning"])
        assert [t["Row"] for t in table] == [2, 2, 3, 3, 4]
        assert [t["Code"] for t in table] == [
            "address_too_few",
            "country_code",
            "address_po_box",
            "duplicate",
            "country_in_address",
        ]
        internal = table[0]
        assert internal["Severity"] == "internal_note"
        assert internal["Decided by"] == "nobody"
        # the control character is dropped rather than failing the save
        assert internal["Note"] == "For the moderator only."

    def test_decisions_and_final_values(self, make_contribution, tmp_path):
        _, _, wb = self._saved(make_contribution, tmp_path)
        by_code = {t["Code"]: t for t in _cleaning_table(wb["Cleaning"])}
        auto = by_code["country_code"]
        assert (auto["Decision"], auto["Final value"], auto["Decided by"]) == (
            "accepted",
            "BD",
            "automatic",
        )
        rejected = by_code["country_in_address"]
        assert rejected["Decision"] == "rejected"
        assert rejected["Final value"] == rejected["Original value"]
        assert rejected["Decided by"] == "contributor"
        assert rejected["Source"] == "rules"
        removal = by_code["duplicate"]
        assert removal["Kind"] == "removal"
        assert removal["Final value"] == "(row removed)"
        flag = by_code["address_po_box"]
        assert flag["Severity"] == "must_fix"
        assert flag["Source"] == "model"

    def test_edited_value_is_the_final_value(self, make_contribution, tmp_path):
        payload = copy.deepcopy(PAYLOAD)
        payload["rows"][2]["suggestions"][0].update(
            decision="EDITED", decided_value="12 Mirpur Road, Dhaka", applied=True
        )
        _, _, wb = self._saved(make_contribution, tmp_path, payload)
        flag = {t["Code"]: t for t in _cleaning_table(wb["Cleaning"])}["address_po_box"]
        assert flag["Final value"] == "12 Mirpur Road, Dhaka"
        assert flag["Decided by"] == "contributor"

    def _nothing_applied(self, closed_reason):
        """The run closed without apply_run: a submission as uploaded, or a
        window that lapsed with the review never opened. Decisions stay as
        they were (the automatic fixes pre-accepted), nothing is applied and
        no row is removed."""
        payload = copy.deepcopy(PAYLOAD)
        payload["run"]["closed_reason"] = closed_reason
        payload["run"]["applied_at"] = None
        for entry in payload["rows"]:
            for s in entry["suggestions"]:
                s["applied"] = False
        df = _frame()
        df["os_hub_cleaning"] = ""
        return payload, df

    def test_submitted_as_uploaded_applies_nothing(self, make_contribution, tmp_path):
        payload, df = self._nothing_applied("submitted")
        _, _, wb = self._saved(make_contribution, tmp_path, payload, df)
        assert _header(wb["Cleaning"])["Outcome"] == (
            "Submitted as uploaded by the contributor"
        )
        by_code = {t["Code"]: t for t in _cleaning_table(wb["Cleaning"])}
        auto = by_code["country_code"]
        assert auto["Decision"] == "accepted (not applied)"
        assert auto["Final value"] == "Bangladesh"
        assert auto["Decided by"] == "automatic"
        removal = by_code["duplicate"]
        assert removal["Decision"] == "accepted (not applied)"
        assert removal["Final value"] == "(row kept)"
        # a rejected fix was never going to be applied, so nothing to say
        assert by_code["country_in_address"]["Decision"] == "rejected"

    def test_lapsed_without_opening_applies_nothing(self, make_contribution, tmp_path):
        payload, df = self._nothing_applied("lapsed")
        _, _, wb = self._saved(make_contribution, tmp_path, payload, df)
        assert _header(wb["Cleaning"])["Outcome"] == (
            "Review window lapsed; review never opened, list as uploaded"
        )

    def test_lapsed_after_opening_says_what_was_applied(self, make_contribution, tmp_path):
        payload = copy.deepcopy(PAYLOAD)
        payload["run"]["closed_reason"] = "lapsed"
        _, _, wb = self._saved(make_contribution, tmp_path, payload)
        assert _header(wb["Cleaning"])["Outcome"] == (
            "Review window lapsed; decisions made so far applied"
        )

    def test_edited_value_not_applied_leaves_the_original(self, make_contribution, tmp_path):
        payload = copy.deepcopy(PAYLOAD)
        payload["rows"][2]["suggestions"][0].update(
            decision="EDITED", decided_value="12 Mirpur Road, Dhaka", applied=False
        )
        _, _, wb = self._saved(make_contribution, tmp_path, payload)
        flag = {t["Code"]: t for t in _cleaning_table(wb["Cleaning"])}["address_po_box"]
        assert flag["Decision"] == "edited (not applied)"
        assert flag["Final value"] == "PO Box 12, Dhaka Division"

    def test_row_links_to_the_cell_on_the_fixes_sheet(self, make_contribution, tmp_path):
        osh, _, wb = self._saved(make_contribution, tmp_path)
        ws = wb["Cleaning"]
        first = osh.cleaning_table_row + 1

        def link(cell):
            h = ws[cell].hyperlink
            return (h.location or h.target or "").lstrip("#")

        assert link(f"A{first}") == f"'{osh.fixessheet}'!C2"
        # the automatic country fix on row 2 points at the country column
        assert link(f"A{first + 1}") == f"'{osh.fixessheet}'!A2"

    def test_summary_and_key_metrics_carry_the_counts(self, make_contribution, tmp_path):
        osh, summary, wb = self._saved(make_contribution, tmp_path)
        assert summary["cleaning"] == {
            "must_fix_unresolved": 1,
            "corrections_rejected": 1,
            "rows_removed": 1,
            "outcome": "submitted",
        }
        metrics = {(s["metric"], s["value"]) for s in osh.statistics}
        assert ("cleaning_must_fix_unresolved", 1) in metrics
        assert ("cleaning_corrections_rejected", 1) in metrics
        values = [c.value for row in wb["Summary"].iter_rows() for c in row]
        assert "cleaning_must_fix_unresolved" in values

    def test_open_window_and_missing_counts_do_not_break_the_sheet(
        self, make_contribution, tmp_path
    ):
        payload = {"run": {"id": 9, "status": "COMPLETE"}, "rows": []}
        osh, summary, wb = self._saved(make_contribution, tmp_path, payload)
        header = _header(wb["Cleaning"])
        assert header["Outcome"] == "Review still open"
        assert header["Suggestions"] == 0
        assert summary["cleaning"]["must_fix_unresolved"] == 0

    def test_formula_like_values_are_escaped(self, make_contribution, tmp_path):
        payload = copy.deepcopy(PAYLOAD)
        payload["rows"][0]["suggestions"][0]["corrected_value"] = "=HYPERLINK(1)"
        _, _, wb = self._saved(make_contribution, tmp_path, payload)
        fix = {t["Code"]: t for t in _cleaning_table(wb["Cleaning"])}["country_in_address"]
        assert fix["Suggested value"] == "'=HYPERLINK(1)"
