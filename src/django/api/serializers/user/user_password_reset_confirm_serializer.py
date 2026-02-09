from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext as _

from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from dj_rest_auth.serializers import PasswordResetConfirmSerializer
from django.db import transaction
from rest_framework.exceptions import ValidationError
from api.models import User


class UserPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    @transaction.atomic
    def save(self):
        self.user.save()

        return self.set_password_form.save()
