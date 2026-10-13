import base64
import binascii
import ipaddress
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests
from django.utils import timezone

from api.models import IdentityRecordAssociation

logger = logging.getLogger(__name__)

# NFR-02 asks that the page render inside three seconds. That is a
# performance target for the whole page, not a timeout for one call, so the
# two numbers are deliberately different. Retrieval makes two sequential
# requests, so this is the budget for each. The threshold is recorded as TBD
# on OSDEV-3583; this is the working value, not a settled one.
RETRIEVAL_TIMEOUT_SECONDS = 5

# Keys the integrity digest has been seen under. The link entries observed
# on the issuer's resolver carry digestMultibase; hash has also been seen,
# mixed within a single facility, so both are accepted rather than one being
# treated as the old spelling.
INTEGRITY_KEYS = ('digestMultibase', 'hash')

ENVELOPED_CREDENTIAL_TYPE = 'EnvelopedVerifiableCredential'
JWT_DATA_URI_PREFIX = 'data:application/vc+jwt,'

REDIRECT_STATUSES = (301, 302, 303, 307, 308)


class RetrievalFailureReason(str, Enum):
    """
    Why a retrieval did not produce a record.

    Typed rather than free text so the page can decide what to show without
    parsing a message, and so a new failure mode cannot quietly render as a
    generic error (AC#3).
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
    A record as retrieved, held in memory for the length of one request.

    Never persisted and never cached. Open Supply Hub stores the association
    and nothing else (NFR-04, scope doc 2.4), which is what makes the
    always-current guarantee hold without synchronization.

    `content` is the decoded credential. `document_uri` is where it actually
    came from, which is a Credential URL: useful for display and support,
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
    Reject a URI that points somewhere this server should not be made to
    fetch.

    The Resolver URI is supplied by a registrant and fetched server side, so
    it is an instruction from outside to make a request from inside.
    Registration is authenticated, which makes abuse unlikely rather than
    impossible. The document URI is worse: it comes from the issuer's
    redirect rather than from anything we stored, so it is checked too.

    Limits worth stating plainly: this blocks literal private, loopback,
    link-local and reserved addresses, and nothing else. A hostname that
    resolves to a private address still passes, because no name resolution
    happens here, and resolving it would not close the gap anyway since the
    address can change between the check and the request. Treat this as
    raising the cost of the obvious mistake, not as egress control. Real
    protection belongs at the network layer.
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
    Pull an integrity digest out of a mapping whichever key it arrived under.

    Checks the top level and one level of nesting. Not a deep search: a
    digest buried arbitrarily deep is more likely a different field that
    happens to share a name than the record's own integrity value.
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
    Read the issuer's own choice of current version out of its redirect.

    The resolver answers a non-link-set request with a redirect to a viewer
    page whose query string carries the document it selected, together with
    that document's digest:

        .../verify?q={"payload":{"uri":"...json","digestMultibase":"..."}}

    Using this is the point. Scope doc 3.5 records that a link-set may list
    many versions under identical titles and that first-listed is not a
    guarantee of currency, so picking one ourselves would be guessing, and
    guessing wrong presents a superseded record as current. The redirect is
    the issuer stating which one is current, so we follow that rather than
    forming an opinion.

    Returns (document_uri, integrity) and tolerates a shape it does not
    recognise by returning (None, None): the caller turns that into a typed
    failure rather than an exception.
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
    Return the credential inside an enveloped verifiable credential.

    The issuer serves records as `EnvelopedVerifiableCredential`, whose
    whole content is a signed JWT held in a data URI. Reading any field of
    the record means decoding that JWT first; the envelope itself carries
    only three keys.

    This decodes and does not verify. Checking the EdDSA signature means
    resolving the issuer's did:web key material, which is a larger piece of
    work and is not what this story is for, and the issuer's own verifier
    page is what performs verification today. Nothing here should be
    presented to a user as verified. The digest alongside the link is the
    tamper check available to us and is carried through unchecked for the
    same reason.

    A document that is not an envelope is returned unchanged, so an issuer
    serving a plain credential still works.
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
    except (ValueError, binascii.Error):
        return None

    return claims if isinstance(claims, dict) else None


def is_encrypted(document):
    """
    Encrypted records are out of scope for the pilot (BRD 8).

    They arrive as a ciphertext envelope rather than a credential, so they
    are detected and reported rather than failing as malformed. At least one
    of the pilot facilities is encrypted today, so this is a real state and
    not a defensive branch.
    """
    return isinstance(document, dict) and 'cipherText' in document


def has_live_record(os_id):
    """
    Whether any record is currently resolving for this identifier.

    Cheap on purpose: an indexed existence check and no outbound call. The
    facility profile uses this to decide whether to offer a link to the
    record, and that page is loaded far more often than the record is read.
    """
    return IdentityRecordAssociation.objects.filter(
        os_id=os_id, live_from__isnull=False
    ).exists()


def get_live_association(os_id):
    """
    The association currently resolving for an OS ID.

    Registration refuses a second live association pointing at a different
    resolver (the 409 in scope doc 3.2), so in practice there is at most
    one. Ordering by most recent is a defensive tiebreak rather than a
    selection rule, and keeps this from depending on row order if that ever
    changes.
    """
    return (
        IdentityRecordAssociation.objects
        .filter(os_id=os_id, live_from__isnull=False)
        .order_by('-live_from')
        .first()
    )


def _get(url, accept, allow_redirects):
    return requests.get(
        url,
        timeout=RETRIEVAL_TIMEOUT_SECONDS,
        allow_redirects=allow_redirects,
        headers={'Accept': accept},
    )


def retrieve_identity_record(os_id):
    """
    Turn an OS ID into the current record content held by its issuer.

    Two requests. The first asks the registered Resolver URI without
    following redirects, because the redirect is how the issuer states which
    version is current. The second fetches the document it named.

    Returns a RetrievalOutcome. Never raises for an upstream problem: an
    issuer being slow, down or serving something unexpected is an expected
    state of the world and the page has to render something for it (AC#3).
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

    try:
        response = _get(resolver_uri, 'application/json', False)
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

    document_uri = None
    integrity = None

    if response.status_code in REDIRECT_STATUSES:
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
            logger.warning(
                'Refused document URI from redirect for %s', os_id
            )
            return _fail(
                RetrievalFailureReason.UNSAFE_URI,
                'The issuer pointed at an address that cannot be fetched.',
            )

        outcome = _fetch_document(os_id, document_uri)
        if isinstance(outcome, RetrievalOutcome):
            return outcome
        document = outcome
    elif response.status_code == 200:
        # An issuer that serves the record straight from the Resolver URI.
        # Not what RBA does, but the contract in 3.3 does not forbid it and
        # treating it as an error would reject a correct implementation.
        try:
            document = response.json()
        except ValueError:
            return _fail(
                RetrievalFailureReason.MALFORMED,
                'The issuer returned a response that is not JSON.',
            )
    else:
        return _fail(
            RetrievalFailureReason.UPSTREAM_ERROR,
            'The issuer returned {}.'.format(response.status_code),
        )

    if is_encrypted(document):
        return _fail(
            RetrievalFailureReason.ENCRYPTED,
            'This record is encrypted. Encrypted records are out of scope '
            'for the pilot.',
        )

    credential = unwrap_credential(document)
    if not isinstance(credential, dict):
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


def _fetch_document(os_id, document_uri):
    """
    Fetch the document the issuer named. Returns the parsed document, or a
    RetrievalOutcome if it could not be fetched.
    """
    try:
        response = _get(document_uri, 'application/json', True)
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
        return response.json()
    except ValueError:
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The record document is not JSON.',
        )
