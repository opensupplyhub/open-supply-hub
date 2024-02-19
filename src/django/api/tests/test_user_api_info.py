from api.serializers.user_api_info_serializer import UserApiInfoSerializer
from rest_framework import status
import json

from api.models import (
    ApiLimit,
    Contributor,
    User,
    RequestLog,
)

from django.test import TestCase
from django.utils import timezone


class UserApiInfoTest(TestCase):
    def setUp(self):
        self.email_one = "one@example.com"
        self.email_two = "two@example.com"
        self.email_three = "three@example.com"
        self.email_four = "four@example.com"
        self.password = "password"
        self.user_one = User.objects.create(email=self.email_one, id=1)
        self.user_one.set_password(self.password)
        self.user_one.save()
        self.user_two = User.objects.create(email=self.email_two, id=2)
        self.user_two.set_password(self.password)
        self.user_two.save()
        self.user_three = User.objects.create(email=self.email_three, id=3)
        self.user_three.set_password(self.password)
        self.user_three.save()
        self.user_four = User.objects.create(email=self.email_four, id=4)
        self.user_four.set_password(self.password)
        self.user_four.save()

        for u in [self.email_one,self.email_two,self.email_three]
            self.client.post(
                "/user-login/",
                {"email": self.email_one, "password": self.password},
                format="json",
            )

        self.yearly_renewal_period = 'YEARLY'
        self.monthly_renewal_period = 'MONTHLY'

        self.url = '/user-api-info/'
        self.IS_NOT_SET = 'Is not set'

        self.contrib_one = Contributor.objects.create(
            id=1,
            admin=self.user_one,
            name="contributor one",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contrib_two = Contributor.objects.create(
            id=2,
            admin=self.user_two,
            name="contributor two",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.contrib_three = Contributor.objects.create(
            id=3,
            admin=self.user_three,
            name="contributor three",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contrib_four = Contributor.objects.create(
            id=4,
            admin=self.user_four,
            name="contributor four",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        now = timezone.now()
        self.limit_one = ApiLimit.objects.create(
            contributor=self.contrib_one,
            period_limit=10,
            period_start_date=now,
            renewal_period=ApiLimit.YEARLY,
        )

        self.limit_two = ApiLimit.objects.create(
            contributor=self.contrib_two,
            period_limit=0,
            period_start_date=now,
            renewal_period=ApiLimit.MONTHLY,
        )

        self.limit_three = ApiLimit.objects.create(
            contributor=self.contrib_three,
            period_limit=0,
            period_start_date=now,
            renewal_period='',
        )

        self.current_usage_one = 10
        self.current_usage_two = 2

        self.expected_content = {
            'apiCallAllowance': '10',
            'currentCallCount': 0,
            'renewalPeriod': 'YEARLY',
        }

        self.serializer_one = UserApiInfoSerializer(self.user_one.id,
                                                    self.contrib_one.id)
        self.serializer_two = UserApiInfoSerializer(self.user_two.id,
                                                    self.contrib_two.id)
        self.serializer_three = UserApiInfoSerializer(
            self.user_three.id, self.contrib_three.id)
        self.serializer_four = UserApiInfoSerializer(
            self.user_four.id, self.contrib_four.id)

    def test_get_api_call_limit(self):
        period_limit_one = self.serializer_one.data['api_call_limit']
        period_limit_two = self.serializer_two.data['api_call_limit']
        period_limit_four = self.serializer_four.data['api_call_limit']

        self.assertEqual(
           str(self.limit_one.period_limit), period_limit_one
        )
        self.assertEqual(
                str(self.limit_two.period_limit), period_limit_two
        )
        self.assertEqual(
                self.IS_NOT_SET, period_limit_four
        )

    def test_get_renewal_period(self):
        renewal_period_one = self.serializer_one.data['renewal_period']
        renewal_period_two = self.serializer_two.data['renewal_period']
        renewal_period_three = self.serializer_three.data['renewal_period']
        self.assertEqual(
            self.yearly_renewal_period, renewal_period_one
        )
        self.assertEqual(
            self.monthly_renewal_period, renewal_period_two
        )
        self.assertEqual(
            self.IS_NOT_SET, renewal_period_three
        )

    def test_get_current_usage(self):
        now = timezone.now()
        for x in range(self.current_usage_one):
            r = RequestLog.objects.create(
                user=self.user_one, response_code=200
            )
            r.created_at = now
            r.save()

        for x in range(self.current_usage_two):
            r = RequestLog.objects.create(
                user=self.user_two, response_code=200
            )
            r.created_at = now
            r.save()
        for x in range(self.current_usage_two):
            r = RequestLog.objects.create(
                user=self.user_three, response_code=500
            )
            r.created_at = now
            r.save()
        current_usage_one = self.serializer_one.data['current_usage']
        current_usage_two = self.serializer_two.data['current_usage']
        current_usage_three = self.serializer_three.data['current_usage']

        self.assertEqual(
            current_usage_one, self.current_usage_one
        )
        self.assertEqual(
            current_usage_two, self.current_usage_two
        )
        self.assertEqual(
            current_usage_three, 0
        )

    def test_user_api_endpoint(self):
        response = self.client.get(
            self.url
            + str(self.user_one.id) + '/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(self.expected_content, content)
