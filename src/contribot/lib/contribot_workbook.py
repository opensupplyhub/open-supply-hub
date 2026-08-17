"""Stage a contributor upload as ``{list_id}.xlsx`` for ContriBot."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Union

import pandas as pd

PathLike = Union[str, Path]


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
            raw = csv_path.read_bytes()
        except OSError as exc:
            raise ValueError(f"Could not read CSV {csv_path.name}: {exc}") from exc

        if not raw.strip():
            raise ValueError(f"CSV file is empty: {csv_path.name}")

        try:
            df = pd.read_csv(
                csv_path,
                encoding="utf-8-sig",
                sep=None,
                engine="python",
                dtype=str,
                keep_default_na=False,
            )
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

        xlsx_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(xlsx_path, index=False, engine="openpyxl")
