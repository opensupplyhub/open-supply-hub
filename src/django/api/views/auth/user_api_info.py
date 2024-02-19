from api.serializers.user_api_info_serializer import UserApiInfoSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


class UserAPIInfo(APIView):
    def get(self, request, uid=None):
        user_api_info_serializer = UserApiInfoSerializer(uid)
        period_limit = user_api_info_serializer.get_api_call_limit()
        renewal_period = user_api_info_serializer.get_renewal_period()
        successful_calls = user_api_info_serializer.get_current_usage()
        api_call_info_data = {
            "apiCallAllowance": period_limit,
            "currentCallCount": successful_calls,
            "renewalPeriod": renewal_period,
        }

        return Response(api_call_info_data)
