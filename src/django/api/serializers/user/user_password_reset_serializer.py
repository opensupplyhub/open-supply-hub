from dj_rest_auth.serializers import PasswordResetSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import EmailField
from django.conf import settings
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
        # Set some values to trigger the send_email method.

        if settings.DEBUG:
            domain_override = 'localhost:6543'
        else:
            domain_override = request.get_host()

        opts = {
            'use_https': not settings.DEBUG,
            'domain_override': domain_override,
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'subject_template_name':
                'mail/reset_user_password_subject.txt',
            'email_template_name':
                'mail/reset_user_password_body.txt',
            'html_email_template_name':
                'mail/reset_user_password_body.html',
        }

        self.reset_form.save(**opts)
