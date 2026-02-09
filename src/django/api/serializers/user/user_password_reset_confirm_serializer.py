from dj_rest_auth.serializers import PasswordResetConfirmSerializer
from django.db import transaction


class UserPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    @transaction.atomic
    def save(self):
        self.user.save()

        return self.set_password_form.save()
