# Identity records API

Endpoints for registering an externally issued record against an OS ID, and
for resolving an OS ID to that record. Built for the RBA / UNTP pilot
(OSDEV-3579 through OSDEV-3607).

These endpoints are **not** in the generated interactive documentation at
`/api/docs/`. The v1 viewsets set `swagger_schema = None`, so the whole v1
API is excluded there by convention and documented separately. This file is
the in-repository reference and the source for the published API
specification at
[opensupplyhub.github.io/open-supply-hub-api-docs](https://opensupplyhub.github.io/open-supply-hub-api-docs).

Section references below are to the OS Hub technical scope document for the
UNTP MVP.

---

## What Open Supply Hub stores

The association between an OS ID and the issuer's **Resolver URI**, and
nothing else. No credential content is copied, cached or re-published
(NFR-04).

The registered value is always a Resolver URI, never a Credential URL. A
Resolver URI resolves to whichever version of a record is current; a
Credential URL points at one specific version. Because the stored value
resolves rather than points, issuing a new version requires no
re-registration (FR-06, FR-11, §3.3).

---

## Register a record

```
POST /api/v1/production-locations/{os_id}/identity-records/
Authorization: Token <key>
Content-Type: application/json
```

```json
{
  "resolver_uri": "https://idr.example.org/api/v4/registry/rbfid/FAC-00000001",
  "record_type": "untp:DigitalFacilityRecord",
  "issuer": "did:web:issuer.example.org",
  "registrant_reference": "FAC-00000001"
}
```

| Field | Required | Notes |
| --- | --- | --- |
| `resolver_uri` | yes | Absolute HTTPS URI. The issuer's resolver link, never a link to one credential version. |
| `record_type` | yes | Max 200 characters. |
| `issuer` | yes | Max 500 characters, for example a `did:web` value. |
| `registrant_reference` | no | The registrant's own identifier for the location, carried through unchanged so they can reconcile against their register. Max 200 characters. Never parsed. |

### Success

```
202 Accepted
```

A repeat of a registration that already exists returns `200` with the
existing registration rather than creating a second one. Retry safety is
the reason: if a registration commits but the response is lost in transit,
the issuer's only sensible move is to retry, and a conflict on that retry
would be indistinguishable from someone else having registered a different
resolver. `200` rather than `202` because nothing was created; a caller
that cares can tell the two apart, and one that does not can treat both as
success.

```json
{
  "moderation_id": "00000000-0000-4000-8000-000000000002",
  "moderation_status": "APPROVED",
  "created_at": "2026-10-08T14:22:10Z",
  "live_from": "2026-10-08T14:22:10Z"
}
```

Pilot-set registrations are live on creation, so no `verification_url` is
issued: there is nothing for the member to confirm (§2.3, §2.5). The
envelope deliberately mirrors the existing production-location submission
API, so this is a new resource on an established pattern.

`moderation_id` is the association's own identifier. The pilot path creates
no moderation event, because the association is Open Supply Hub's own
construction rather than something asserted and awaiting review. The field
keeps its name so the envelope matches the established one.

### Failures

| Status | Meaning |
| --- | --- |
| `400` | Malformed body, or `resolver_uri` is not an absolute HTTPS URI, or it looks like a Credential URL rather than a Resolver URI |
| `401` | Token missing or invalid |
| `404` | Identifier not found on this instance |
| `409` | This identifier already has a live association with a **different** Resolver URI |

Every failure leaves the member's record itself issued and gives something
specific to retry.

#### One difference from §3.2 worth knowing about

**`422` is not implemented.** §3.2 lists it for "well formed but not
resolvable here", which §3.4 ties to identifiers issued only on a private
instance. On a given instance an identifier either exists or it does not, so
that condition currently returns `404`. The read side answers the same
condition the same way; see the resolver section below.

### Credential URL detection

A `resolver_uri` ending in `.json` is rejected with `400`. Registering a
Credential URL would point at one specific version and silently break the
always-current guarantee, which is the premise of the pilot.

This catches the obvious mistake and nothing more. A Credential URL served
without a `.json` suffix would pass.

---

## Read a registration's state

```
GET /api/v1/production-locations/{os_id}/identity-records/{moderation_id}/
Authorization: Token <key>
```

Returns the same envelope as the registration response: the current state
and, once live, the time from which it resolves. `404` if there is no such
registration for that identifier. A malformed `moderation_id` is a miss
rather than an error.

---

## Read the registered record

```
GET /api/v1/production-locations/{os_id}/identity-record/
```

Note the singular `identity-record`. This returns the *content* of whichever
record is currently live for the identifier, fetched from the issuer at the
moment of the call and never stored.

Reachable by the web client, which is what the identity-record page uses. It
is deliberately not opened wider: the resolver points third parties at the
page and at the issuer's own resolver, not at this endpoint.

### Available

```json
{
  "os_id": "XX2000001AAAAA5",
  "available": true,
  "resolver_uri": "https://idr.example.org/api/v4/registry/rbfid/FAC-00000001",
  "document_uri": "https://documents.example.org/....json",
  "record_type": "untp:DigitalFacilityRecord",
  "issuer": "did:web:issuer.example.org",
  "registrant_reference": "FAC-00000001",
  "retrieved_at": "2026-10-13T09:14:02Z",
  "integrity": { "algorithm": "digestMultibase", "value": "zQm..." },
  "credential": { "...": "the decoded credential, passed through unmapped" }
}
```

`credential` is the decoded credential exactly as the issuer published it.
It is not flattened or mapped: which fields are shown, and under what
labels, is a presentation decision rather than one this layer should fix.

`document_uri` is where the content actually came from, which is a Credential
URL. It is useful for display and support and is deliberately not stored.

**The credential is decoded, not verified.** Checking the signature requires
resolving the issuer's `did:web` key material, which is separate work.
Nothing from this endpoint may be presented to a user as verified.

### Not available

```json
{
  "os_id": "XX2000001AAAAA5",
  "available": false,
  "reason": "timeout",
  "detail": "The issuer did not respond within 5 seconds."
}
```

This is a `200`, not an error status. The request to Open Supply Hub did not
fail; the issuer's did. The page has to render something either way, and the
typed reason lets it say which rather than showing a generic error for a
record that exists and is merely unreachable.

| `reason` | Meaning |
| --- | --- |
| `not_registered` | No live record is registered for this identifier |
| `timeout` | The issuer did not respond within the threshold |
| `unreachable` | The issuer could not be reached |
| `upstream_error` | The issuer returned a non-200 |
| `malformed` | The response could not be read as a record |
| `encrypted` | The record is encrypted; out of scope for the pilot (BRD §8) |
| `unsafe_uri` | The registered or returned address is not fetchable |

### How retrieval works

Two requests. The first asks the Resolver URI **without following
redirects**, because the issuer's redirect is how it states which version is
current; the document and its digest are read out of that redirect. The
second fetches the document named there and decodes it.

The version is never chosen by Open Supply Hub. §3.5 records that a link-set
may list many versions under identical titles and that first-listed is not a
guarantee of currency, so choosing would mean guessing, and guessing wrong
would present a superseded record as current.

Records are served as an `EnvelopedVerifiableCredential` whose content is a
signed JWT in a data URI. Reading any field means decoding it first. An
issuer serving a plain credential directly is also accepted.

The working timeout is **5 seconds per request**. NFR-02's three seconds is
a page-render target rather than a timeout, so the two numbers differ
deliberately. The threshold is recorded as TBD on OSDEV-3583.

---

## Resolve an identifier

```
GET /osid/{os_id}
```

Public. One path, two behaviours, chosen by the `Accept` header.

| `Accept` | Response |
| --- | --- |
| `application/linkset+json` | `200` with an RFC 9264 link-set |
| anything else, including absent | `302` to the relevant page |

The link-set is an explicit opt-in. A bare request, including the `*/*` that
command line clients send by default, behaves like a browser and redirects.

An `Accept` header naming something unsupported does not produce a `406`. An
identifier anyone may hold and paste into any client should resolve rather
than be refused on those grounds.

### Redirect target

| Condition | Target |
| --- | --- |
| A record is registered | `/facilities/{os_id}/identity-record` |
| No record is registered | `/facilities/{os_id}` |

The second is FR-14 and is a normal response, not an error state.

A superseded OS ID keeps resolving. Merged identifiers follow the alias on
read (§2.7).

### Failures

| Status | Meaning |
| --- | --- |
| `400` | Not a well-formed OS ID. Checked before any database lookup |
| `404` | Well formed, but not resolvable on this instance |

The `404` body states the identifier is **not resolvable here** rather than
that it is invalid, because it may be valid on another instance. The same
response is returned whether an identifier was never issued anywhere or
exists only on a private instance, so the two cannot be distinguished from
outside (§3.4, NFR-08, AC-09).

Error bodies are always JSON, whatever the caller asked for.

### Link relation types

Link-set keys are link relation types drawn from a vocabulary Open Supply
Hub publishes itself.

There is no central registry to take them from. The UNTP 0.7.0 context
defines `linkType` as a plain string and enumerates no values, and the
reference resolver implementation documents the convention: an
implementation ships defaults based on GS1 standards and otherwise declares
its own vocabulary at a resolvable namespace. Two terms are published:

| Term | Meaning |
| --- | --- |
| `productionLocation` | The Open Supply Hub page for this location. Always present. |
| `registeredRecord` | A record registered against this identifier by its issuer. Present only when one is live. |

The entry for a registered record carries the issuer's **Resolver URI**,
never a link to one version, and there is never more than one. Which
version is current stays the issuer's decision, which is what keeps the
always-current guarantee true without re-registration.

Links are served both in the body and in an HTTP `Link` header.

```
GET /api/v1/voc/
GET /api/v1/voc/?show=linktypes
```

Public. The machine-readable description of those terms, which is what the
keys in a link-set dereference to. The resolver description document names
this namespace in `namespaceURI` and `profileUrl`, so a client can find it
without being told out of band.

---

## Resolver description

```
GET /.well-known/resolver
```

Public. Describes what this resolver answers for, so a client can discover
the identifier path rather than hard-coding it. Minimal by design; the full
ISO 18975 vocabulary is settled alongside the relation type names.

---

## Deployment note

`/osid/*` and `/.well-known/*` are root-level paths and need explicit
routing at the content delivery layer, or they fall through to the
single-page application. See `deployment/terraform/cdn.tf` and OSDEV-3607.
