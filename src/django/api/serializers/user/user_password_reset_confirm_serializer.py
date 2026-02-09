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
    def validate(self, attrs):
        uidb64 = attrs.get("uid")
        token = attrs.get("token")
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uidb64))
        except Exception:
            raise ValidationError({"uid": _("Invalid value")})
        try:
            self.user = User.objects.get(pk=uid_decoded)
        except User.DoesNotExist:
            raise ValidationError({"uid": _("Invalid value")})

        # Validate token manually to avoid re-decoding in the parent.
        if not default_token_generator.check_token(self.user, token):
            raise ValidationError({"token": _("Invalid token")})

        self.set_password_form = SetPasswordForm(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise ValidationError(self.set_password_form.errors)

        return attrs

    @transaction.atomic
    def save(self):
        self.user.save()

        return self.set_password_form.save()
