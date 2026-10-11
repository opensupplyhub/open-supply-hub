import ipaddress
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

import requests
from django.utils import timezone

from api.models import IdentityRecordAssociation

logger = logging.getLogger(__name__)

# NFR-02 asks that the page render inside three seconds. That is a
# performance target for the whole page, not a timeout for this one call, so
# the two numbers are deliberately different. Five seconds is long enough
# that a merely slow issuer is not reported as a broken one, and short enough
# that a hung request does not hold a worker indefinitely. The threshold is
# recorded as TBD on OSDEV-3583; this is the working value, not a settled one.
RETRIEVAL_TIMEOUT_SECONDS = 5

# Keys the integrity digest has been seen under on the issuer's records.
# Older entries use digestMultibase and newer ones use hash, mixed within a
# single facility, so both are accepted rather than one being migrated to the
# other (AC#2).
INTEGRITY_KEYS = ('digestMultibase', 'hash')


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
    """

    os_id: str
    resolver_uri: str
    record_type: str
    issuer: str
    registrant_reference: str
    retrieved_at: object
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
    Reject a Resolver URI that points somewhere this server should not be
    made to fetch.

    The URI is supplied by a registrant and fetched server side, so it is an
    instruction from outside to make a request from inside. Registration is
    authenticated, which makes abuse unlikely rather than impossible.

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
    Pull the integrity digest out of a record whichever key it arrived under.

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


def get_live_association(os_id):
    """
    The association currently resolving for an OS ID.

    Registration refuses a second live association pointing at a different
    resolver (the 409 in scope doc 3.2), so in practice there is at most one.
    Ordering by most recent is a defensive tiebreak rather than a selection
    rule, and keeps this from depending on row order if that ever changes.
    """
    return (
        IdentityRecordAssociation.objects
        .filter(os_id=os_id, live_from__isnull=False)
        .order_by('-live_from')
        .first()
    )


def retrieve_identity_record(os_id):
    """
    Turn an OS ID into the current record content held by its issuer.

    Follows the registered Resolver URI and returns whatever the issuer's
    resolver returns. It deliberately does not read a link-set and choose a
    version: scope doc 3.5 records that a link-set may list many versions
    under identical titles and that first-listed is not a guarantee of
    currency. Choosing here would mean guessing, and guessing wrong would
    show a superseded record as current, which is the one thing the
    always-current guarantee exists to prevent.

    Returns a RetrievalOutcome. Never raises for an upstream problem: an
    issuer being slow or down is an expected state of the world and the page
    has to render something for it (AC#3).
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
            'Refused to retrieve identity record for %s: unsafe URI',
            os_id,
        )
        return _fail(
            RetrievalFailureReason.UNSAFE_URI,
            'The registered Resolver URI is not a fetchable HTTPS address.',
        )

    try:
        response = requests.get(
            resolver_uri,
            timeout=RETRIEVAL_TIMEOUT_SECONDS,
            allow_redirects=True,
            headers={'Accept': 'application/json'},
        )
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

    if response.status_code != 200:
        return _fail(
            RetrievalFailureReason.UPSTREAM_ERROR,
            'The issuer returned {}.'.format(response.status_code),
        )

    try:
        payload = response.json()
    except ValueError:
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The issuer returned a response that is not JSON.',
        )

    if not isinstance(payload, dict):
        return _fail(
            RetrievalFailureReason.MALFORMED,
            'The issuer returned JSON that is not a record object.',
        )

    return RetrievalOutcome(
        record=RetrievedRecord(
            os_id=os_id,
            resolver_uri=resolver_uri,
            record_type=association.record_type,
            issuer=association.issuer,
            registrant_reference=association.registrant_reference,
            retrieved_at=timezone.now(),
            integrity=find_integrity(payload),
            # Carried through rather than mapped field by field. The page
            # design settles which fields are shown and under what labels,
            # so mapping here would fix a presentation decision in the
            # service before it has been made. Normalization at this layer
            # is limited to what varies between issuers' records, which
            # today is the integrity key.
            content=payload,
        )
    )
