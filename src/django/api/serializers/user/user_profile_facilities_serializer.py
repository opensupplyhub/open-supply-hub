from rest_framework.serializers import BooleanField, Serializer


class UserProfileFacilitiesSerializer(Serializer):
    """Serializer for the user profile facilities endpoint."""
    spotlight = BooleanField(required=False, default=False)
