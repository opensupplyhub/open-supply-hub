from allauth.account.utils import complete_signup
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from django.db import transaction

from ...models import Contributor, User, FacilityDownloadLimit
from ...serializers import UserSerializer
from .add_user_to_mailing_list import add_user_to_mailing_list


class SubmitNewUserForm(CreateAPIView):
    serializer_class = UserSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(request)
            pk = serializer.data['id']
            user = User.objects.get(pk=pk)

            name = request.data.get('name')
            description = request.data.get('description')
            website = request.data.get('website')
            contrib_type = request.data.get('contributor_type')
            other_contrib_type = request.data.get('other_contributor_type')

            if name is None:
                raise ValidationError('name cannot be blank')

            if '|' in name:
                raise ValidationError('name cannot contain the "|" character')

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

            Contributor.objects.create(
                admin=user,
                name=name,
                description=description,
                website=website,
                contrib_type=contrib_type,
                other_contrib_type=other_contrib_type,
            )

            FacilityDownloadLimit.get_or_create_user_download_limit(user)

            if user.should_receive_newsletter:
                add_user_to_mailing_list(user.email, name, contrib_type)

            complete_signup(self.request._request, user, 'optional', None)

            return Response(status=HTTP_204_NO_CONTENT)
