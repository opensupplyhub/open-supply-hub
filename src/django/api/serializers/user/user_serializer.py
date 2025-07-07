from allauth.account.utils import setup_user_email
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)
from api.constants import FacilityClaimStatuses, FacilitiesDownloadSettings
from waffle import switch_is_active
from django.contrib.auth import password_validation
from django.core import exceptions

from ...models import Contributor, FacilityClaim, User, FacilityDownloadLimit
from ..embed_config import EmbedConfigSerializer


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)
    email = EmailField()
    name = SerializerMethodField()
    description = SerializerMethodField()
    website = SerializerMethodField()
    contributor_type = SerializerMethodField()
    other_contributor_type = SerializerMethodField()
    contributor_id = SerializerMethodField()
    embed_config = SerializerMethodField()
    claimed_facility_ids = SerializerMethodField()
    embed_level = SerializerMethodField()
    allowed_records_number = SerializerMethodField()

    class Meta:
        model = User
        exclude = ()

    def validate(self, data):
        user = User(**data)
        password = data.get('password')

        try:
            password_validation.validate_password(password=password, user=user)
            return super(UserSerializer, self).validate(data)
        except exceptions.ValidationError as exc:
            raise ValidationError({"password": list(exc.messages)}) from exc

    def validate_email(self, email):
        users = User.objects.filter(email__iexact=email)
        if users:
            raise ValidationError("A user with that email already exists.")

        return email.lower()

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def save(self, request, **kwargs):
        user = super(UserSerializer, self).save()
        setup_user_email(request, user, [])
        return user

    def get_name(self, user):
        try:
            return user.contributor.name
        except Contributor.DoesNotExist:
            return None

    def get_description(self, user):
        try:
            return user.contributor.description
        except Contributor.DoesNotExist:
            return None

    def get_website(self, user):
        try:
            return user.contributor.website
        except Contributor.DoesNotExist:
            return None

    def get_contributor_type(self, user):
        try:
            return user.contributor.contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_other_contributor_type(self, user):
        try:
            return user.contributor.other_contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_contributor_id(self, user):
        try:
            return user.contributor.id
        except Contributor.DoesNotExist:
            return None

    def get_embed_config(self, user):
        try:
            return EmbedConfigSerializer(user.contributor.embed_config).data
        except Contributor.DoesNotExist:
            return None

    def get_embed_level(self, user):
        try:
            return user.contributor.embed_level
        except Contributor.DoesNotExist:
            return None

    def get_claimed_facility_ids(self, user):
        if not switch_is_active('claim_a_facility'):
            return {
                'approved': None,
                'pending': None,
            }

        try:
            approved = (
                FacilityClaim
                .objects
                .filter(status=FacilityClaimStatuses.APPROVED)
                .filter(contributor=user.contributor)
                .values_list('facility__id', flat=True)
            )
            pending = (
                FacilityClaim
                .objects
                .filter(status=FacilityClaimStatuses.PENDING)
                .filter(contributor=user.contributor)
                .values_list('facility__id', flat=True)
            )
            return {
                'pending': pending,
                'approved': approved,
            }
        except Contributor.DoesNotExist:
            return {
                'approved': None,
                'pending': None,
            }

    def get_allowed_records_number(self, user):
        try:
            limit = FacilityDownloadLimit.objects.get(user=user)
            return limit.free_download_records + limit.paid_download_records
        except FacilityDownloadLimit.DoesNotExist:
            return FacilitiesDownloadSettings.FREE_FACILITIES_DOWNLOAD_LIMIT
