from api.partner_data_file_upload.constants import (
    DEVELOPER_ERROR_HINTS,
    DEVELOPER_PROCESSING_ERROR_PREFIX,
)


def format_developer_processing_error(message: str) -> str:
    message = (message or "").strip()
    if message.startswith(DEVELOPER_PROCESSING_ERROR_PREFIX):
        return message
    return f"{DEVELOPER_PROCESSING_ERROR_PREFIX}{message}"


def format_upload_processing_error(error: Exception) -> str:
    """
    Sheet or list issues stay as-is for moderators. Infrastructure,
    configuration, and unexpected failures are prefixed so moderators
    know to contact developers.
    """
    message = str(error).strip()
    if isinstance(error, ValueError):
        if any(hint in message for hint in DEVELOPER_ERROR_HINTS):
            return format_developer_processing_error(message)
        return message
    return format_developer_processing_error(message)
