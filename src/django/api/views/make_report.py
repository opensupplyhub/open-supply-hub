import sys

from django.conf import settings


def _make_report(**extra_data):
    if getattr(settings, 'ROLLBAR', {}):
        import rollbar
        rollbar.report_exc_info(
            sys.exc_info(),
            extra_data=extra_data
        )


def _report_facility_claim_email_error_to_rollbar(claim):
    _make_report(claim_id=claim.id)


def _report_hubspot_error_to_rollbar(email, name, contrib_type, error_text):
    _make_report(
        email=email,
        name=name,
        contrib_type=contrib_type,
        error_text=error_text
    )
