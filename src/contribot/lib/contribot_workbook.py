"""Stage a contributor upload as ``{list_id}.xlsx`` for ContriBot."""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import Union

import pandas as pd

logger = logging.getLogger(__name__)

PathLike = Union[str, Path]

# Mirrors ``openpyxl.cell.cell.ILLEGAL_CHARACTERS_RE``: control characters
# 0-8, 11-12 and 14-31, which openpyxl refuses to write into a worksheet. Tab
# (9), newline (10) and carriage return (13) are legal and pass through.
ILLEGAL_CHARACTERS_RE = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")

# Control characters in a facility list are debris from a bad encoding
# conversion upstream of the upload: 0x1A (SUB) is what a transcoder emits
# when a character will not map into the target codepage, so a name reaching
# us as "HAZIR G\x1aY\x1aM" was "HAZIR GIYIM" before someone exported it
# through a non-Unicode encoding. The original letters are unrecoverable, so
# substitute U+FFFD rather than deleting them -- stripping would silently
# publish "HAZIR GYM", whereas the replacement character trips ContriBot's
# C0007 unusual-character check and puts the damaged cell in front of a
# moderator.
CONTROL_CHARACTER_REPLACEMENT = "�"


class ContribotWorkbook:
    """Convert or copy an uploaded facility list into a ContriBot workbook.

    CSV uploads are converted to Excel. Native ``.xlsx`` uploads are copied so
    the processed Drive report is always ``{list_id}.~PROCESSED.xlsx``.
    """

    SUPPORTED_SUFFIXES = {".csv", ".xlsx"}

    def __init__(self, work_dir: PathLike, source_path: PathLike, list_id: str):
        self._work_dir = Path(work_dir)
        self._source_path = Path(source_path)
        self._list_id = str(list_id).strip()
        if not self._list_id:
            raise ValueError("list_id is required")

    def transform(self) -> Path:
        """Return a workbook path named ``{list_id}.xlsx`` for ContriBot."""
        suffix = self._source_path.suffix.lower()
        if suffix not in self.SUPPORTED_SUFFIXES:
            raise ValueError(
                f"ContriBot requires a .csv or .xlsx file; got {self._source_path.name!r}"
            )

        dest = self._work_dir / f"{self._list_id}.xlsx"
        if suffix == ".csv":
            self._csv_to_xlsx(dest)
            return dest

        if self._source_path.resolve() != dest.resolve():
            shutil.copy2(self._source_path, dest)
        return dest

    def _csv_to_xlsx(self, xlsx_path: Path) -> None:
        """Convert a UTF-8 CSV (optional BOM, sniffed delimiter) to ``.xlsx``.

        Empty files, header-only files, non-UTF-8 encoding, and parse errors
        raise ``ValueError`` so Step Functions can catch the failure for notify.
        """
        csv_path = self._source_path
        try:
            if csv_path.stat().st_size == 0:
                raise ValueError(f"CSV file is empty: {csv_path.name}")
            df = pd.read_csv(
                csv_path,
                encoding="utf-8-sig",
                sep=None,
                engine="python",
                dtype=str,
                keep_default_na=False,
            )
        except OSError as exc:
            raise ValueError(f"Could not read CSV {csv_path.name}: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise ValueError(f"CSV is not valid UTF-8: {csv_path.name}") from exc
        except pd.errors.EmptyDataError as exc:
            raise ValueError(f"CSV file is empty: {csv_path.name}") from exc
        except pd.errors.ParserError as exc:
            raise ValueError(f"CSV is malformed: {csv_path.name}: {exc}") from exc

        if df.columns.size == 0:
            raise ValueError(f"CSV has no columns: {csv_path.name}")
        if df.empty:
            raise ValueError(f"CSV has no data rows: {csv_path.name}")

        df = df.map(
            lambda value: f"'{value}"
            if isinstance(value, str) and value.startswith("=")
            else value
        )
        self._replace_illegal_characters(df)
        xlsx_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(xlsx_path, index=False, engine="openpyxl")

    def _replace_illegal_characters(self, df: pd.DataFrame) -> None:
        """Replace worksheet-illegal control characters in ``df``, in place.

        Without this, one damaged cell makes ``to_excel`` raise
        ``IllegalCharacterError`` and the whole list fails to process -- and
        openpyxl names only the first offending cell, so fixing that one just
        surfaces the next. Headers are cleaned too: ``to_excel`` writes those
        into the sheet as well.
        """
        damaged: list[str] = []

        def clean(value: str) -> str:
            return ILLEGAL_CHARACTERS_RE.sub(CONTROL_CHARACTER_REPLACEMENT, value)

        def is_damaged(value: object) -> bool:
            return isinstance(value, str) and bool(ILLEGAL_CHARACTERS_RE.search(value))

        if any(is_damaged(column) for column in df.columns):
            damaged.extend(
                f"header {column!r}" for column in df.columns if is_damaged(column)
            )
            df.columns = [
                clean(column) if isinstance(column, str) else column
                for column in df.columns
            ]

        for column in df.columns:
            values = df[column].tolist()
            positions = [
                position for position, value in enumerate(values) if is_damaged(value)
            ]
            if not positions:
                continue
            for position in positions:
                # +2: one for the header row, one because sheets are 1-indexed.
                damaged.append(f"row {position + 2} column {column!r}")
                values[position] = clean(values[position])
            df[column] = values

        if damaged:
            shown = damaged[:20]
            suffix = "" if len(damaged) == len(shown) else f" (+{len(damaged) - len(shown)} more)"
            logger.warning(
                "List %s: replaced control characters from a bad encoding "
                "conversion in %s cell(s): %s%s",
                self._list_id,
                len(damaged),
                "; ".join(shown),
                suffix,
            )
