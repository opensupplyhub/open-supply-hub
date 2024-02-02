import json

import requests
from django.conf import settings

from ..make_report import _report_hubspot_error_to_rollbar

HUBSPOT_ROOT = 'https://api.hubapi.com'
HUBSPOT_CONTACT_URL = HUBSPOT_ROOT + '/crm/v3/objects/contacts'
HUBSPOT_SUBSCRIBE_URL = HUBSPOT_ROOT + \
    '/communication-preferences/v3/subscribe'
OSHUB_LEGAL_BASIS = (
    "<p>Open Apparel Registry, Inc., doing business as "
    "Open Supply Hub, is committed to protecting and respecting your "
    "privacy, and we’ll only use your personal information to administer "
    "your account and to provide the products and services you requested "
    "from us. From time to time, we would like to contact you about our "
    "products and services, as well as other content that may be of "
    "interest to you. If you consent to us contacting you for this "
    "purpose, please tick below to confirm:</p>\n<p>I agree to receive "
    "communications from Open Apparel Registry, Inc., doing business as "
    "Open Supply Hub.</p>"
)


def add_user_to_mailing_list(email, name, contrib_type):
    try:
        if settings.HUBSPOT_API_KEY is None:
            return None

        headers = {
            'Authorization': f"Bearer {settings.HUBSPOT_API_KEY}",
            'Content-Type': 'application/json'
        }

        # Add new contact
        new_contact = json.dumps({
            "properties": {
                "company": name,
                "email": email,
            }
        })
        response = requests.post(
                HUBSPOT_CONTACT_URL,
                headers=headers,
                data=new_contact
        )

        # Raise error for error statuses other than existing contact
        contact_already_exists = response.status_code == 409
        if not contact_already_exists:
            response.raise_for_status()

        # Set new contact subscription type
        subscription = json.dumps({
            "emailAddress": email,
            "subscriptionId": settings.HUBSPOT_SUBSCRIPTION_ID,
            "status": "SUBSCRIBED",
            "sourceOfStatus": "SUBSCRIPTION_STATUS",
            "legalBasis": "CONSENT_WITH_NOTICE",
            "legalBasisExplanation": OSHUB_LEGAL_BASIS
        })
        response = requests.post(
                HUBSPOT_SUBSCRIBE_URL,
                headers=headers,
                data=subscription
        )

        # Raise error for error statuses other than existing subscription
        is_already_subscribed = response.status_code == 400 and \
            'is already subscribed' in response.text
        if not is_already_subscribed:
            response.raise_for_status()

    except Exception:
        _report_hubspot_error_to_rollbar(
            email, name, contrib_type, response.text
        )
