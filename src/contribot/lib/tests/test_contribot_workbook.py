"""Unit tests for :class:`contribot_workbook.ContribotWorkbook`."""

from __future__ import annotations

import pandas as pd
import pytest

from contribot_workbook import ContribotWorkbook


def test_transform_copies_xlsx_to_list_id_name(tmp_path):
    source = tmp_path / "Summer.xlsx"
    source.write_bytes(b"xlsx-bytes")

    dest = ContribotWorkbook(
        work_dir=tmp_path, source_path=source, list_id="77"
    ).transform()

    assert dest == tmp_path / "77.xlsx"
    assert dest.read_bytes() == b"xlsx-bytes"
    assert source.exists()


def test_transform_xlsx_already_named_for_list_id_is_unchanged(tmp_path):
    source = tmp_path / "77.xlsx"
    source.write_bytes(b"xlsx-bytes")

    dest = ContribotWorkbook(
        work_dir=tmp_path, source_path=source, list_id="77"
    ).transform()

    assert dest == source
    assert dest.read_bytes() == b"xlsx-bytes"


def test_transform_csv_comma_separated(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_text("country,name,address\nBangladesh,Acme,1 Main St\n")

    dest = ContribotWorkbook(
        work_dir=tmp_path, source_path=csv_path, list_id="101"
    ).transform()

    assert dest == tmp_path / "101.xlsx"
    df = pd.read_excel(dest, dtype=str)
    assert list(df.columns) == ["country", "name", "address"]
    assert df.iloc[0]["name"] == "Acme"


def test_transform_csv_utf8_bom_and_semicolon(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_bytes(
        b"\xef\xbb\xbfcountry;name;address\nGermany;Werk 1;Hauptstr. 1\n"
    )

    dest = ContribotWorkbook(
        work_dir=tmp_path, source_path=csv_path, list_id="101"
    ).transform()

    df = pd.read_excel(dest, dtype=str)
    assert list(df.columns) == ["country", "name", "address"]
    assert df.iloc[0]["country"] == "Germany"


def test_transform_csv_tab_delimited(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_text("country\tname\taddress\nIndia\tMill\t2 Lane\n")

    dest = ContribotWorkbook(
        work_dir=tmp_path, source_path=csv_path, list_id="5"
    ).transform()

    df = pd.read_excel(dest, dtype=str)
    assert df.iloc[0]["name"] == "Mill"


def test_transform_csv_uppercase_suffix(tmp_path):
    csv_path = tmp_path / "LIST.CSV"
    csv_path.write_text("country,name,address\nVietnam,Plant,3 Rd\n")

    dest = ContribotWorkbook(
        work_dir=tmp_path, source_path=csv_path, list_id="8"
    ).transform()

    assert dest == tmp_path / "8.xlsx"
    df = pd.read_excel(dest, dtype=str)
    assert df.iloc[0]["country"] == "Vietnam"


def test_transform_csv_creates_work_dir(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_text("country,name,address\nKenya,Site,4 Ave\n")
    work_dir = tmp_path / "nested" / "work"

    dest = ContribotWorkbook(
        work_dir=work_dir, source_path=csv_path, list_id="12"
    ).transform()

    assert dest == work_dir / "12.xlsx"
    assert dest.is_file()


def test_transform_raises_for_empty_csv(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_bytes(b"")

    with pytest.raises(ValueError, match="CSV file is empty"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=csv_path, list_id="99"
        ).transform()


def test_transform_raises_for_whitespace_only_csv(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_bytes(b"  \n\n")

    with pytest.raises(ValueError, match="CSV has no data rows"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=csv_path, list_id="99"
        ).transform()


def test_transform_raises_for_header_only_csv(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_text("country,name,address\n")

    with pytest.raises(ValueError, match="CSV has no data rows"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=csv_path, list_id="99"
        ).transform()


def test_transform_raises_for_malformed_csv(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_bytes(b'country,name\n"unclosed quote,Acme\n')

    with pytest.raises(ValueError, match="CSV is malformed"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=csv_path, list_id="99"
        ).transform()


def test_transform_raises_for_non_utf8_csv(tmp_path):
    csv_path = tmp_path / "list.csv"
    csv_path.write_bytes(b"country,name,address\n" + "München".encode("latin-1") + b"\n")

    with pytest.raises(ValueError, match="not valid UTF-8"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=csv_path, list_id="99"
        ).transform()


def test_transform_raises_when_csv_is_unreadable(tmp_path):
    missing = tmp_path / "missing.csv"

    with pytest.raises(ValueError, match="Could not read CSV"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=missing, list_id="99"
        ).transform()


def test_transform_raises_for_unsupported_extension(tmp_path):
    source = tmp_path / "list.txt"
    source.write_text("nope")

    with pytest.raises(ValueError, match="requires a .csv or .xlsx"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=source, list_id="99"
        ).transform()


def test_init_requires_list_id(tmp_path):
    with pytest.raises(ValueError, match="list_id is required"):
        ContribotWorkbook(
            work_dir=tmp_path, source_path=tmp_path / "list.xlsx", list_id="  "
        )
