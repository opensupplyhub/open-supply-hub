# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_auth.views import LoginView


class APICallInfo(LoginView):
    def get(self, request, *args, **kwargs):
        print("!!!!")
        return Response({
            "apiCallAllowance": '0',
            "currentCallCount": '0',
            "renewalPeriod": '0',
        })
    #         contributor_logs = RequestLog.objects.filter(
    #         response_code__gte=200,
    #         response_code__lte=299).annotate(
    #             contributor=F('user__contributor__id')
    #         ).values('contributor').annotate(
    #             log_dates=ArrayAgg('created_at')
    #         )
    # for c in contributor_logs:
    #     check_contributor_api_limit(at_datetime, c)

        # if not request.user.has_groups:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        # try:
        #     token = Token.objects.get(user=request.user)

        #     token_data = {
        #         'token': token.key,
        #         'created': token.created.isoformat(),
        #     }

        #     return Response(token_data)
        # except Token.DoesNotExist as exc:
        #     raise NotFound() from exc

