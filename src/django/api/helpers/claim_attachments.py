import os
import uuid

from django.utils.text import slugify
from rest_framework.exceptions import ValidationError as DRFValidationError

from api.models.facility.facility_claim_attachments import (
    FacilityClaimAttachments
)
from oar.settings import (
    ALLOWED_ATTACHMENT_EXTENSIONS,
    MAX_ATTACHMENT_AMOUNT,
    MAX_ATTACHMENT_SIZE_IN_BYTES,
)

# Leading bytes ("magic bytes") for every allowed attachment type. The
# extension check alone is spoofable: a file named report.pdf that is
# actually HTML would otherwise be stored and later served from our
# origin. Signatures per file format specifications.
FILE_SIGNATURES = {
    '.jpg': (b'\xff\xd8\xff',),
    '.jpeg': (b'\xff\xd8\xff',),
    '.png': (b'\x89PNG\r\n\x1a\n',),
    '.pdf': (b'%PDF-',),
}

_MAX_SIGNATURE_LENGTH = max(
    len(signature)
    for signatures in FILE_SIGNATURES.values()
    for signature in signatures
)


def validate_file_content(file):
    '''
    Verify that a file's leading bytes match the signature its extension
    claims. Raises DRFValidationError on mismatch. Leaves the file
    position at the start.
    '''
    extension = os.path.splitext(file.name)[-1].lower()
    signatures = FILE_SIGNATURES.get(extension)
    if signatures is None:
        raise DRFValidationError(
            f"{file.name} has an unsupported file type."
        )

    file.seek(0)
    leading_bytes = file.read(_MAX_SIGNATURE_LENGTH)
    file.seek(0)

    if not any(
        leading_bytes.startswith(signature) for signature in signatures
    ):
        raise DRFValidationError(
            f"The content of {file.name} does not match its file type."
        )


def validate_attachment_files(files, existing_count=0):
    '''
    Validate a batch of uploaded attachment files: total count across the
    claim's lifetime, extension allowlist, per-file size limit, and file
    content (magic bytes). `existing_count` is the number of attachments
    the claim already has, so the MAX_ATTACHMENT_AMOUNT cap holds across
    submission plus any later edits, not per request.
    '''
    if existing_count + len(files) > MAX_ATTACHMENT_AMOUNT:
        raise DRFValidationError(
            f"Maximum {MAX_ATTACHMENT_AMOUNT} attachments allowed."
        )

    for file in files:
        extension = os.path.splitext(file.name)[-1].lower()
        if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
            raise DRFValidationError(
                f"{file.name} has an unsupported file type."
            )

        if file.size > MAX_ATTACHMENT_SIZE_IN_BYTES:
            raise DRFValidationError(
                f"{file.name} exceeds the 5MB size limit."
            )

        validate_file_content(file)

    return files


def create_claim_attachment(file, facility_claim):
    '''
    Store one uploaded file as an attachment of the given claim.

    The storage key is an opaque UUID (plus the validated extension)
    rather than the user-supplied filename: object keys propagate into
    access logs, CloudTrail and error traces, so they must never carry
    names or other personal data. The original filename is kept in the
    file_name column for display.
    '''
    file_name, file_extension = os.path.splitext(file.name)
    display_name = f'{slugify(file_name, allow_unicode=True)}{file_extension}'

    file.name = f'{uuid.uuid4().hex}{file_extension.lower()}'

    return FacilityClaimAttachments.objects.create(
        claim=facility_claim,
        file_name=display_name[:200],
        claim_attachment=file,
    )


def delete_claim_attachment(attachment):
    '''
    Delete an attachment row and its stored file together. The single
    deletion path for attachments: claimant self-service delete, claim
    cascade, and any future retention job must all go through here (or
    through the model cascade, which removes the file via the
    post_delete signal).
    '''
    attachment.delete()
