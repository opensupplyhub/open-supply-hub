"""Process a single facility list: validate, upload report, return notify payload.

Downloads the uploaded ``.csv`` or ``.xlsx`` from S3, converts CSV to a workbook
named ``{list_id}.xlsx`` so ContriBot writes ``{list_id}.~PROCESSED.xlsx``,
runs validation using the bundled error-codes config, uploads the report to
Google Drive, and returns stats for the notify step.
"""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from lib.contribot import ContriBot
from lib.contribot_workbook import ContribotWorkbook
from lib.google_drive import GoogleDrive
from lib.lists_repository import STATUS_FAILED, STATUS_PROCESSING, ListsRepository
from lib.s3_storage import S3Storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """Lambda entry point: validate one facility list and upload its report."""
    list_id = str(event.get("list_id", "")).strip()
    if not list_id:
        raise ValueError("event.list_id is required")

    repository = ListsRepository()
    item = repository.get_list(list_id)
    if not item:
        raise ValueError(f"No DynamoDB row for list_id={list_id}")

    work_dir = Path("/tmp") / "contribot" / list_id

    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)

    try:
        file_name = (item.get("file_name") or "").strip()
        if not file_name:
            raise ValueError(f"list_id={list_id} is missing file_name")

        work_dir.mkdir(parents=True, exist_ok=True)
        source_path = work_dir / Path(file_name).name
        output_dir = work_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        repository.update_list(list_id, status=STATUS_PROCESSING)
        logger.info("Processing list_id=%s file_name=%s", list_id, file_name)

        s3 = S3Storage()
        s3.download(file_name, str(source_path))
        if not source_path.is_file():
            raise RuntimeError(f"S3 download produced no file at {source_path}")

        config_path = str(
            Path(__file__).resolve().parent / "lib" / "0000.error_codes.xlsx"
        )
        if not os.path.isfile(config_path):
            raise RuntimeError(f"Error-codes workbook not found at {config_path}")

        contribot_workbook = ContribotWorkbook(
            work_dir=work_dir,
            source_path=source_path,
            list_id=list_id,
        )
        workbook_path = contribot_workbook.transform()
        bot = ContriBot(str(workbook_path), config_file=config_path)
        bot.process()
        summary = bot.save(targetfolder=str(output_dir))

        report_path = output_dir / bot.targetfilename
        if not report_path.is_file():
            raise RuntimeError(f"ContriBot did not write report at {report_path}")

        drive = GoogleDrive()
        report_url = drive.upload_file(str(report_path))
        num_lines = int(summary["num_lines"])
        num_errors = int(summary["num_errors"])
        error_ratio = float(summary["error_ratio"])

        repository.update_list(
            list_id,
            report_url=report_url,
            num_lines=num_lines,
            num_errors=num_errors,
            error_ratio=error_ratio,
        )

        logger.info(
            "Processed list_id=%s lines=%s errors=%s ratio=%.4f",
            list_id,
            num_lines,
            num_errors,
            error_ratio,
        )

        return {
            "list_id": list_id,
            "report_url": report_url,
            "num_lines": num_lines,
            "num_errors": num_errors,
            "error_ratio": error_ratio,
        }
    except Exception:
        logger.exception("Failed processing list_id=%s", list_id)
        repository.update_list(list_id, status=STATUS_FAILED)
        raise
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
