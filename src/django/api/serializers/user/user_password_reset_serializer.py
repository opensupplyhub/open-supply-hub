from dj_rest_auth.serializers import PasswordResetSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import EmailField
from allauth.account.forms import ResetPasswordForm

from ...models import User


class UserPasswordResetSerializer(PasswordResetSerializer):
    email = EmailField()
    password_reset_form_class = ResetPasswordForm

    def validate_email(self, user_email):
        data = self.initial_data
        self.reset_form = self.password_reset_form_class(data=data)
        if not self.reset_form.is_valid():
            raise ValidationError("Error")

        if not User.objects.filter(email__iexact=user_email).exists():
            raise ValidationError("Error")

        return user_email

    def save(self):
        request = self.context.get('request')
        self.reset_form.save(request=request)
