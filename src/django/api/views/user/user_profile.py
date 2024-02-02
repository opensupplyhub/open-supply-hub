from rest_framework.decorators import permission_classes
from rest_framework.exceptions import (
    NotFound,
    ValidationError,
)
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from django.contrib.auth import login, password_validation
from django.contrib.auth.hashers import check_password
from django.core.exceptions import (
    PermissionDenied,
    ValidationError as dValidationError,
)

from ...models import Contributor, User
from ...permissions import IsRegisteredAndConfirmed
from ...serializers import UserProfileSerializer


class UserProfile(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get(self, request, pk=None, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            response_data = UserProfileSerializer(user).data
            return Response(response_data)
        except User.DoesNotExist as exc:
            raise NotFound() from exc

    def patch(self, request, pk, *args, **kwargs):
        pass

    @permission_classes((IsRegisteredAndConfirmed,))
    def put(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        if not request.user.did_register_and_confirm_email:
            raise PermissionDenied

        try:
            user_for_update = User.objects.get(pk=pk)

            if request.user != user_for_update:
                raise PermissionDenied

            current_password = request.data.get('current_password', '')
            new_password = request.data.get('new_password', '')
            confirm_new_password = request.data.get('confirm_new_password', '')

            if current_password != '' and new_password != '':
                if new_password != confirm_new_password:
                    raise ValidationError(
                        'New password and confirm new password do not match')

                if not check_password(current_password,
                                      user_for_update.password):
                    raise ValidationError('Your current password is incorrect')

                try:
                    password_validation.validate_password(
                        password=new_password, user=user_for_update)
                except dValidationError as exc:
                    raise ValidationError({
                        "new_password": list(exc.messages)
                    }) from exc

            name = request.data.get('name')
            description = request.data.get('description')
            website = request.data.get('website')
            contrib_type = request.data.get('contributor_type')
            other_contrib_type = request.data.get('other_contributor_type')
            is_moderation_mode = request.data.get('is_moderation_mode')

            if name is None:
                raise ValidationError('name cannot be blank')

            if '|' in name:
                raise ValidationError('Name cannot contain the "|" character.')

            if description is None:
                raise ValidationError('description cannot be blank')

            if contrib_type is None:
                raise ValidationError('contributor type cannot be blank')

            if contrib_type == Contributor.OTHER_CONTRIB_TYPE:
                if other_contrib_type is None or len(other_contrib_type) == 0:
                    raise ValidationError(
                        "contributor type description required for Contributor"
                        " Type 'Other'"
                    )

            if (is_moderation_mode is True
                    and (user_for_update.is_staff is False
                         or user_for_update.is_superuser is False)):
                raise ValidationError(
                    "moderation mode feature available only"
                    " for 'Moderator'"
                )

            user_contributor = request.user.contributor
            user_contributor.name = name
            user_contributor.description = description
            user_contributor.website = website
            user_contributor.contrib_type = contrib_type
            user_contributor.other_contrib_type = other_contrib_type
            user_contributor.save()

            if new_password != '':
                user_for_update.set_password(new_password)

            user_for_update.is_moderation_mode = is_moderation_mode

            user_for_update.save()

            # Changing the password causes the user to be logged out, which we
            # don't want
            if new_password != '':
                login(request, user_for_update)

            response_data = UserProfileSerializer(user_for_update).data
            return Response(response_data)
        except User.DoesNotExist as exc:
            raise NotFound() from exc
        except Contributor.DoesNotExist as exc:
            raise NotFound() from exc
