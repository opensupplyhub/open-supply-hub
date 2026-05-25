"""
Serializer for the partner group contributors endpoint.
Specifies the fields returned by GET /api/partner-group-contributors/.
"""

from rest_framework import serializers


class PartnerGroupContributorsSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    label = serializers.CharField(source='name')
    contributors = serializers.SerializerMethodField()

    def get_contributors(self, obj):
        seen = {}
        for field in getattr(obj, 'active_fields', []):
            for contributor in field.contributor_set.all():
                seen[contributor.id] = contributor.name
        return [{'id': cid, 'name': name} for cid, name in seen.items()]
