"""Process a single facility list: validate, upload report, return notify payload.

Downloads the uploaded ``.csv`` or ``.xlsx`` from S3, converts CSV to a workbook
named ``{list_id}.xlsx`` so ContriBot writes ``{list_id}.~PROCESSED.xlsx``,
runs validation using the bundled error-codes config, uploads the report to
Google Drive, and returns stats for the notify step.

When the list went through the contributor's list-cleaning review (OSDEV-3726
v3) the report is of the list as the contributor left it, read from the
platform rather than S3, and gains a Cleaning sheet listing every suggestion
and what was done with it (OSDEV-3398). A list whose review window is still
open is not processed: it is left for the retry schedule with
:class:`ListUnderReview`, which the state machine catches without a failure
notification, and the wait does not count as a processing attempt.
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
from lib.os_hub_api import OSHubAPI
from lib.s3_storage import S3Storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ListUnderReview(RuntimeError):
    """The contributor can still change the list, so there is nothing final to report on."""


def os_hub_api() -> OSHubAPI | None:
    """The platform client, or ``None`` where this Lambda has no API access.

    Without it the report is of the upload as stored in S3, as before
    OSDEV-3398, which is also what the list-cleaning kill switch leaves.
    """
    if os.environ.get("OS_HUB_API_URL") and os.environ.get(
        "OS_HUB_API_TOKEN_SECRET_ARN"
    ):
        return OSHubAPI()
    logger.warning(
        "OS_HUB_API_URL / OS_HUB_API_TOKEN_SECRET_ARN not set; "
        "reporting on the upload as stored"
    )
    return None


def cleaning_state(api: OSHubAPI, list_id: str) -> dict | None:
    """The list's completed cleaning run, or ``None`` when the report is of the upload.

    No run, or a run that failed, means the list goes to moderation as
    uploaded. A window that is still open raises :class:`ListUnderReview`:
    ``fetch_lists`` waits out the window before enqueueing, so this only fires
    when a parse took longer than that margin allowed for.
    """
    payload = api.fetch_cleaning(list_id)
    run = payload.get("run")
    if not run:
        return None
    if payload.get("window_open"):
        raise ListUnderReview(
            f"List {list_id} is still being reviewed by its contributor "
            f"(until {run.get('review_until')}); it will be processed once "
            "the review window has closed."
        )
    if run.get("status") != "COMPLETE":
        logger.info(
            "List %s cleaning run %s is %s; reporting on the upload as stored",
            list_id,
            run.get("id"),
            run.get("status"),
        )
        return None
    return payload


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

        api = os_hub_api()
        cleaning = cleaning_state(api, list_id) if api is not None else None
        if cleaning is not None:
            # The list as the contributor left it, every row where it was
            # uploaded, removed rows tagged rather than dropped.
            source_path = work_dir / f"{list_id}-cleaned.csv"
            api.download_cleaned_list(list_id, source_path)
            logger.info(
                "List %s: reporting on the post-review list (cleaning run %s)",
                list_id,
                (cleaning.get("run") or {}).get("id"),
            )
        else:
            s3 = S3Storage()
            s3.download(file_name, str(source_path))
        if not source_path.is_file():
            raise RuntimeError(f"Download produced no file at {source_path}")

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
        if cleaning is not None:
            bot.attach_cleaning(cleaning)
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
            # None when the list did not go through the cleaning review
            "cleaning": summary.get("cleaning"),
        }
    except ListUnderReview as exc:
        # Waiting is not a failure. The row goes back to FAILED because that
        # is what retry_failed_lists scans, and the attempt it counted for
        # this run is given back so the wait costs none of
        # CONTRIBOT_MAX_ATTEMPTS; earlier real failures keep their count.
        # The state machine catches this error by name and skips the
        # failure notification.
        logger.info("Leaving list_id=%s for a later run: %s", list_id, exc)
        repository.update_list(
            list_id,
            status=STATUS_FAILED,
            attempt_count=max(0, int(item.get("attempt_count") or 0) - 1),
        )
        raise
    except Exception:
        logger.exception("Failed processing list_id=%s", list_id)
        repository.update_list(list_id, status=STATUS_FAILED)
        raise
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
