import base64
import ipaddress
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from django.db.models import Q
from django.utils import timezone

from api.models import IdentityRecordAssociation
from api.models.facility.facility_alias import FacilityAlias

logger = logging.getLogger(__name__)

# Per request, and retrieval makes two sequential requests. Separate from
# the three-second page-render target, which covers the whole page rather
# than one call.
RETRIEVAL_TIMEOUT_SECONDS = 10

# Redirect hops allowed on the document fetch. The issuer's own
# resolver takes one; more than a couple means something is wrong.
MAX_REDIRECT_HOPS = 3

# A record is a credential, not a payload. Anything larger is either a
# mistake or an attempt to exhaust the worker reading it.
MAX_DOCUMENT_BYTES = 2 * 1024 * 1024

# Spellings an encrypted envelope has been seen under. UNTP uses
# cipherText; a JWE in JSON serialization uses ciphertext alongside
# protected and recipients. Missing one means rendering ciphertext as
# though it were the record.
ENCRYPTION_KEYS = ('cipherText', 'ciphertext', 'recipients')

# A record can carry a cryptographic hash of its own content, so a reader
# can tell whether what it fetched is what the issuer published. Issuers
# name that hash inconsistently: digestMultibase and hash both appear, mixed
# within a single facility, so both are read rather than one being treated
# as the old spelling.
INTEGRITY_KEYS = ('digestMultibase', 'hash')

ENVELOPED_CREDENTIAL_TYPE = 'EnvelopedVerifiableCredential'
JWT_DATA_URI_PREFIX = 'data:application/vc+jwt,'

REDIRECT_STATUSES = (301, 302, 303, 307, 308)


class RetrievalFailureReason(str, Enum):
    """
    Why a retrieval did not produce a record.

    Typed rather than free text so the page can decide what to show without
    parsing a message, and so a new failure mode cannot quietly render as a
    generic error.
    """

    NOT_REGISTERED = 'not_registered'
    UNSAFE_URI = 'unsafe_uri'
    TIMEOUT = 'timeout'
    UNREACHABLE = 'unreachable'
    UPSTREAM_ERROR = 'upstream_error'
    MALFORMED = 'malformed'
    ENCRYPTED = 'encrypted'


@dataclass(frozen=True)
class RetrievalFailure:
    reason: RetrievalFailureReason
    detail: str


@dataclass(frozen=True)
class RetrievedRecord:
    """
    A record as retrieved, held in memory for the length of one request
    and never persisted. `content` is the decoded credential;
    `document_uri` is the Credential URL it came from, kept for display
    and deliberately not stored.
    """

    os_id: str
    resolver_uri: str
    record_type: str
    issuer: str
    registrant_reference: str
    retrieved_at: object
    document_uri: Optional[str]
    integrity: Optional[dict]
    content: dict


@dataclass(frozen=True)
class RetrievalOutcome:
    record: Optional[RetrievedRecord] = None
    failure: Optional[RetrievalFailure] = None

    @property
    def ok(self):
        return self.record is not None


def _fail(reason, detail):
    return RetrievalOutcome(failure=RetrievalFailure(reason, detail))


def is_safe_resolver_uri(uri):
    """
    Reject a URI pointing somewhere this server should not be made to
    fetch, since it is supplied from outside and fetched server side.
    Blocks literal private, loopback, link-local and reserved addresses
    only, so treat it as raising the cost of the obvious mistake rather
    than as egress control.
    """
    parsed = urlparse(uri)

    if parsed.scheme != 'https':
        return False

    host = parsed.hostname
    if not host:
        return False

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        # A hostname rather than a literal address. See the docstring.
        return True

    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
    )


def find_integrity(payload):
    """
    Pull an integrity digest out of a mapping whichever key it arrived
    under. Checks the top level and one level of nesting only, since a
    digest buried deeper is more likely a different field sharing a
    name.
    """
    if not isinstance(payload, dict):
        return None

    for key in INTEGRITY_KEYS:
        value = payload.get(key)
        if value:
            return {'algorithm': key, 'value': value}

    for nested in payload.values():
        if not isinstance(nested, dict):
            continue
        for key in INTEGRITY_KEYS:
            value = nested.get(key)
            if value:
                return {'algorithm': key, 'value': value}

    return None


def parse_resolver_redirect(location):
    """
    Read the issuer's own choice of current version out of its redirect,
    which names the selected document and its digest. Following that
    choice avoids picking a version ourselves and presenting a
    superseded record as current; an unrecognized shape returns (None,
    None) for the caller to turn into a typed failure.
    """
    if not location:
        return None, None

    query = parse_qs(urlparse(location).query)
    raw = (query.get('q') or [None])[0]
    if not raw:
        return None, None

    try:
        envelope = json.loads(raw)
    except ValueError:
        return None, None

    if not isinstance(envelope, dict):
        return None, None

    payload = envelope.get('payload')
    if not isinstance(payload, dict):
        return None, None

    uri = payload.get('uri')
    if not isinstance(uri, str) or not uri:
        return None, None

    return uri, find_integrity(payload)


def unwrap_credential(document):
    """
    Return the credential inside an `EnvelopedVerifiableCredential`,
    whose content is a signed JWT that must be decoded before any field
    can be read. This decodes and does not verify, so nothing here may
    be presented to a user as verified; a document that is not an
    envelope is returned unchanged.
    """
    if not isinstance(document, dict):
        return None

    types = document.get('type')
    types = [types] if isinstance(types, str) else (types or [])

    if ENVELOPED_CREDENTIAL_TYPE not in types:
        # Not an envelope. An issuer serving a plain credential is fine.
        return document

    identifier = document.get('id', '')
    if (
        not isinstance(identifier, str)
        or not identifier.startswith(JWT_DATA_URI_PREFIX)
    ):
        # It says it is an envelope but carries nothing we can open.
        # Returning it unchanged would present the envelope itself as the
        # record, which is worse than reporting that it cannot be read.
        return None

    token = identifier[len(JWT_DATA_URI_PREFIX):]
    segments = token.split('.')
    if len(segments) < 2:
        return None

    encoded = segments[1]
    try:
        raw = base64.urlsafe_b64decode(
            encoded + '=' * (-len(encoded) % 4)
        )
        claims = json.loads(raw)
    except ValueError:
        # base64 raises binascii.Error, which is a ValueError.
        return None

    return claims if isinstance(claims, dict) else None


def is_encrypted(document):
    """
    Encrypted records are out of scope for the pilot and arrive as a
    ciphertext envelope rather than a credential. They are detected and
    reported rather than failing as malformed, since at least one pilot
    facility is encrypted today.
    """
    if not isinstance(document, dict):
        return False

    return any(key in document for key in ENCRYPTION_KEYS)


def _looks_like_credential(candidate):
    """
    Whether this is a credential rather than merely some JSON.

    Without this, an issuer answering 200 with an error object has that
    object rendered as the record. Checked loosely, by the two markers a
    verifiable credential always carries, so an unfamiliar but valid
    record still reads.
    """
    if not isinstance(candidate, dict):
        return False

    if 'credentialSubject' in candidate:
        return True

    declared = candidate.get('type') or candidate.get('@type') or []
    if isinstance(declared, str):
        declared = [declared]

    return any('Credential' in str(entry) for entry in declared)


def _identifier_filter(os_id):
    """
    Match an association registered against this identifier or against any
    identifier that now resolves to the same location.

    A merge turns the superseded OS ID into a FacilityAlias and leaves this
    table untouched, so a record registered before the merge is still the
    surviving location's record and has to be found from either identifier.
    One query with two subqueries, because the facility profile asks this
    on every view.
    """
    return (
        Q(os_id=os_id)
        | Q(os_id__in=FacilityAlias.objects
            .filter(facility_id=os_id).values('os_id'))
        | Q(os_id__in=FacilityAlias.objects
            .filter(pk=os_id).values('facility_id'))
    )


def has_live_record(os_id):
    """
    Whether any record is currently resolving for this identifier. Cheap
    on purpose, an indexed existence check with no outbound call,
    because the facility profile calls it far more often than the record
    is read.
    """
    return IdentityRecordAssociation.objects.filter(
        _identifier_filter(os_id), live_from__isnull=False
    ).exists()


def get_live_association(os_id):
    """
    The association currently resolving for an OS ID. Registration
    refuses a second live association pointing at a different resolver,
    so ordering by most recent is a defensive tiebreak rather than a
    selection rule.
    """
    return (
        IdentityRecordAssociation.objects
        .filter(_identifier_filter(os_id), live_from__isnull=False)
        .order_by('-live_from')
        .first()
    )


class _UnsafeRedirect(Exception):
    """A redirect pointed somewhere this server must not fetch."""


class _TooManyRedirects(Exception):
    """The issuer redirected past the hop limit."""


def _get(url, accept, allow_redirects):
    return requests.get(
        url,
        timeout=RETRIEVAL_TIMEOUT_SECONDS,
        allow_redirects=allow_redirects,
        headers={'Accept': accept},
    )


def _follow_safely(url):
    """
    Fetch a URL, checking every redirect target rather than only the
    first. requests would follow the chain itself, which would let an
    issuer reach a private address one hop after the check.
    """
    for _ in range(MAX_REDIRECT_HOPS + 1):
        response = _get(url, 'application/json', False)

        if response.status_code not in REDIRECT_STATUSES:
            return response

        location = response.headers.get('Location')
        if not location:
            return response

        url = urljoin(url, location)
        if not is_safe_resolver_uri(url):
            raise _UnsafeRedirect(url)

    raise _TooManyRedirects(url)


def _read_json(response):
    """
    Parse a response body, refusing one too large to hold in memory. The
    body comes from a third party named by a registrant, so its size is
    not ours to trust.
    """
    declared = response.headers.get('Content-Length')
    if declared and declared.isdigit() and int(declared) > MAX_DOCUMENT_BYTES:
        raise _DocumentTooLarge(declared)

    if len(response.content) > MAX_DOCUMENT_BYTES:
        raise _DocumentTooLarge(len(response.content))

    return response.json()


class _DocumentTooLarge(Exception):
    """The issuer's document exceeded the size we are willing to read."""


def retrieve_identity_record(os_id):
    """
    Turn an OS ID into the current record content held by its issuer, in
    two requests: the registered Resolver URI without following
    redirects, then the document its redirect names. Returns a
    RetrievalOutcome and never raises for an upstream problem, since a
    slow or unavailable issuer is an expected state the page still has
    to render.
    """
    association = get_live_association(os_id)

    if association is None:
        return _fail(
            RetrievalFailureReason.NOT_REGISTERED,
            'No live record is registered for this identifier.',
        )

    resolver_uri = association.resolver_uri

    if not is_safe_resolver_uri(resolver_uri):
        logger.warning(
            'Refused to retrieve identity record for %s: unsafe URI', os_id
        )
        return _fail(
            RetrievalFailureReason.UNSAFE_URI,
            'The registered Resolver URI is not a fetchable HTTPS address.',
        )

    response = _ask_resolver(os_id, resolver_uri)
    if isinstance(response, RetrievalOutcome):
        return response

    resolved = _document_from_response(os_id, response)
    if isinstance(resolved, RetrievalOutcome):
        return resolved
    document, document_uri, integrity = resolved

    if is_encrypted(document):
        return _fail(
            RetrievalFailureReason.ENCRYPTED,
            'This record is encrypted. Encrypted records are out of scope '
            'for the pilot.',
        )

    credential = unwrap_credential(document)
    if not _looks_like_credential(credential):
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The issuer returned something that is not a readable record.',
        )

    return RetrievalOutcome(
        record=RetrievedRecord(
            os_id=os_id,
            resolver_uri=resolver_uri,
            record_type=association.record_type,
            issuer=association.issuer,
            registrant_reference=association.registrant_reference,
            retrieved_at=timezone.now(),
            document_uri=document_uri,
            integrity=integrity or find_integrity(credential),
            # Carried through rather than mapped field by field. The page
            # design settles which fields are shown and under what labels,
            # so mapping here would fix a presentation decision in the
            # service before it has been made. Normalization at this layer
            # is limited to what varies between issuers: the envelope and
            # where the digest lives.
            content=credential,
        )
    )


def _ask_resolver(os_id, resolver_uri):
    """
    Make the first request, without following redirects. Returns the
    response, or a RetrievalOutcome if the issuer could not be reached.
    """
    try:
        return _get(resolver_uri, 'application/json', False)
    except requests.Timeout:
        return _fail(
            RetrievalFailureReason.TIMEOUT,
            'The issuer did not respond within {} seconds.'.format(
                RETRIEVAL_TIMEOUT_SECONDS
            ),
        )
    except requests.RequestException as exc:
        logger.warning(
            'Identity record retrieval failed for %s: %s', os_id, exc
        )
        return _fail(
            RetrievalFailureReason.UNREACHABLE,
            'The issuer could not be reached.',
        )


def _document_from_response(os_id, response):
    """
    Turn the resolver's answer into a document, following its redirect
    where there is one. Returns a (document, document_uri, integrity)
    triple, or a RetrievalOutcome if there is nothing readable.
    """
    if response.status_code in REDIRECT_STATUSES:
        return _document_from_redirect(os_id, response)

    if response.status_code == 200:
        # An issuer that serves the record straight from the Resolver URI.
        # Not what the November pilot's issuer does, but nothing forbids it
        # and treating it as an error would reject a correct implementation.
        try:
            return _read_json(response), None, None
        except _DocumentTooLarge:
            return _fail(
                RetrievalFailureReason.MALFORMED,
                'The issuer returned a response too large to read.',
            )
        except ValueError:
            return _fail(
                RetrievalFailureReason.MALFORMED,
                'The issuer returned a response that is not JSON.',
            )

    return _fail(
        RetrievalFailureReason.UPSTREAM_ERROR,
        'The issuer returned {}.'.format(response.status_code),
    )


def _document_from_redirect(os_id, response):
    """
    Follow the issuer's redirect to the document it named. Returns a
    (document, document_uri, integrity) triple, or a RetrievalOutcome.
    """
    document_uri, integrity = parse_resolver_redirect(
        response.headers.get('Location')
    )

    if not document_uri:
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The issuer redirected somewhere this cannot read a record '
            'from.',
        )

    if not is_safe_resolver_uri(document_uri):
        logger.warning('Refused document URI from redirect for %s', os_id)
        return _fail(
            RetrievalFailureReason.UNSAFE_URI,
            'The issuer pointed at an address that cannot be fetched.',
        )

    outcome = _fetch_document(os_id, document_uri)
    if isinstance(outcome, RetrievalOutcome):
        return outcome

    return outcome, document_uri, integrity


def _fetch_document(os_id, document_uri):
    """
    Fetch the document the issuer named. Returns the parsed document, or a
    RetrievalOutcome if it could not be fetched.
    """
    try:
        response = _follow_safely(document_uri)
    except _UnsafeRedirect:
        logger.warning('Refused a redirect target for %s', os_id)
        return _fail(
            RetrievalFailureReason.UNSAFE_URI,
            'The issuer redirected to an address that cannot be fetched.',
        )
    except _TooManyRedirects:
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The issuer redirected too many times.',
        )
    except requests.Timeout:
        return _fail(
            RetrievalFailureReason.TIMEOUT,
            'The record document did not arrive within {} seconds.'.format(
                RETRIEVAL_TIMEOUT_SECONDS
            ),
        )
    except requests.RequestException as exc:
        logger.warning(
            'Identity record document fetch failed for %s: %s', os_id, exc
        )
        return _fail(
            RetrievalFailureReason.UNREACHABLE,
            'The record document could not be reached.',
        )

    if response.status_code != 200:
        return _fail(
            RetrievalFailureReason.UPSTREAM_ERROR,
            'The record document returned {}.'.format(response.status_code),
        )

    try:
        return _read_json(response)
    except _DocumentTooLarge:
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The record document is too large to read.',
        )
    except ValueError:
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The record document is not JSON.',
        )
