"""
Waffle switches gating the UNTP identity record pilot
(OSDEV-3579 .. OSDEV-3607).

Registration is the write side: an issuer naming a Resolver URI against an
OS ID. It needs to open first, so the pilot records can be registered in a
deployed environment and checked there, while nothing about them is
reachable from outside.

Resolution is the read side: the public resolver, its description, the link
type vocabulary, the identity record page and the entry point to it. Opening
this is the announcement. It makes `/osid/{os_id}` answer for every OS ID on
the instance, not only the handful carrying a registered record, so it is the
switch that wants a deliberate decision behind it rather than a deploy.

Both default to off.
"""

# The public resolver, /.well-known/resolver, the link type vocabulary, the
# identity record page and its content endpoint, and the flag on the facility
# profile that offers the link.
IDENTITY_RESOLVER_SWITCH = 'enable_identity_resolver'

# Registering a record against an OS ID, and reading the state of a
# registration.
IDENTITY_RECORD_REGISTRATION_SWITCH = 'enable_identity_record_registration'
