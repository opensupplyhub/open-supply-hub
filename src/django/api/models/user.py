import uuid
from allauth.account.models import EmailAddress

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.core.validators import RegexValidator
from django.db import models

from api.constants import FeatureGroups
from api.constants import OriginSource


def get_default_rate(rate):
    return settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'][rate]


def get_default_burst_rate():
    return get_default_rate("burst")


def get_default_sustained_rate():
    return get_default_rate("sustained")


def get_default_data_upload_rate():
    return get_default_rate("data_upload")


throttle_rate_validator = RegexValidator(
    r"\d+/(second|minute|hour|day)",
    "You must enter value of the format N/(second|minute|hour|day)"
)


class EmailAsUsernameUserManager(BaseUserManager):
    """
    A custom user manager which uses emails as unique identifiers for auth
    instead of usernames.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    objects = EmailAsUsernameUserManager()

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the user.'
    )
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        ('active'),
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    is_moderation_mode = models.BooleanField(
        ('moderation mode'),
        default=False,
        help_text=(
            'The ability to activate the Moderation features mode.'
        ),
    )

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        help_text='Unique email address used as a username'
    )
    username = models.CharField(max_length=20, null=True, blank=True)
    should_receive_newsletter = models.BooleanField(
        default=False,
        help_text='User has asked to receive the newsletter'
    )
    has_agreed_to_terms_of_service = models.BooleanField(
        default=False,
        help_text='User has agreed to the terms of service'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    burst_rate = models.CharField(
        default=get_default_rate('burst'),
        max_length=20,
        validators=[throttle_rate_validator],
        help_text=(
            "Maximum allowed burst requests for this user. "
            "Burst rate should be shorter periods, 'second' or 'minute'. "
            "This applies to most API requests, but excludes Facility uploads."
        )
    )
    sustained_rate = models.CharField(
        default=get_default_rate('sustained'),
        max_length=20,
        validators=[throttle_rate_validator],
        help_text=(
            "Maximum allowed sustained requests for this user. "
            "Sustained rate should be longer periods, 'hour' or 'day'. "
            "This applies to most API requests, but excludes Facility uploads."
        )
    )
    data_upload_rate = models.CharField(
        default=get_default_rate('data_upload'),
        max_length=20,
        validators=[throttle_rate_validator],
        help_text=(
            "Maximum allowed facility upload rate for this user. "
            "This applies to only API Facility uploads."
        )
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        blank=True,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def first_name(self):
        pass

    def last_name(self):
        pass

    @property
    def did_register_and_confirm_email(self):
        try:
            email_address = EmailAddress.objects.get_primary(self.id)

            if email_address:
                return email_address.verified

        # if no EmailAddress record exists, the User was created through the
        # Django admin rather than the UI. Treat this User as verified.
            return True
        except EmailAddress.DoesNotExist:
            return True

    @property
    def can_submit_privately(self):
        return self.groups.filter(
            name=FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY
        ).exists()

    @property
    def can_view_full_contrib_details(self):
        if self.can_submit_privately:
            return self.groups.filter(
                name=FeatureGroups.CAN_VIEW_FULL_CONTRIB_DETAIL
            ).exists()

        return True

    @property
    def has_contributor(self):
        return hasattr(self, 'contributor')

    @property
    def has_groups(self):
        return self.groups.count() > 0
