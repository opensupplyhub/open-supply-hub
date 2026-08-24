"""Slack notification body for a processed ContriBot facility list."""

from __future__ import annotations

from typing import Any, Optional


class NotifyMessage:
    """Assemble the Slack text for one facility-list notification."""

    ERROR_RATIO_EMOJIS = [
        (0.05, ":simple_smile:"),
        (0.25, ":confused:"),
    ]
    ERROR_RATIO_FALLBACK_EMOJI = ":disappointed:"

    def __init__(
        self,
        *,
        list_id: str,
        base_url: str,
        list_name: str = "",
        contributor_id: Optional[str] = None,
        contributor_name: str = "",
        contributor_email: str = "",
        file_name: str = "",
        report_url: Optional[str] = None,
        num_lines: Any = None,
        num_errors: Any = None,
        error_ratio: Any = None,
        error: Optional[dict] = None,
    ) -> None:
        self._list_id = list_id
        self._base_url = base_url.rstrip("/")
        self._list_name = list_name
        self._contributor_id = contributor_id
        self._contributor_name = contributor_name
        self._contributor_email = contributor_email
        self._file_name = file_name
        self._report_url = report_url
        self._num_lines = num_lines
        self._num_errors = num_errors
        self._error_ratio = error_ratio
        self._error = error

    def generate(self) -> str:
        """Return the Slack message text."""
        list_link = (
            f"<{self._base_url}/lists/{self._list_id}|#{self._list_id} "
            f"{self._list_name}".rstrip()
            + ">"
        )
        headline = (
            f":rotating_light: ContriBot failed to process list {list_link}"
            if self._error
            else f"New list {list_link}"
        )
        lines = [
            headline,
            self._contributor_line(),
            f"File {self._file_name}" if self._file_name else "",
            f"<{self._report_url}|Checked report>" if self._report_url else "",
            self._error_ratio_line(),
            self._error_line(),
        ]
        return "\n".join(line for line in lines if line)

    def _contributor_line(self) -> str:
        if not (self._contributor_name or self._contributor_email):
            return ""

        contributor = f"Contributor {self._contributor_name}"
        if self._contributor_id:
            admin_link = (
                f"{self._base_url}/admin/api/contributor/"
                f"{self._contributor_id}/change/"
            )
            contributor = f"<{admin_link}|{contributor}>"
        return f"{contributor} email {self._contributor_email}".rstrip()

    def _error_ratio_line(self) -> str:
        if (
            self._num_lines is None
            or self._num_errors is None
            or self._error_ratio is None
        ):
            return ""

        error_ratio = float(self._error_ratio)
        emoji = self.ERROR_RATIO_FALLBACK_EMOJI
        for threshold, threshold_emoji in self.ERROR_RATIO_EMOJIS:
            if error_ratio < threshold:
                emoji = threshold_emoji
                break
        return (
            f"({self._num_lines}/{self._num_errors}) "
            f"Error ratio: {error_ratio:.1%} {emoji}"
        )

    def _error_line(self) -> str:
        if not self._error:
            return ""
        cause = self._error.get("Cause") or self._error.get("Error") or ""
        return f"Error: {cause[:500]}" if cause else ""
