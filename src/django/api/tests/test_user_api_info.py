from api.views.auth.user_api_info import (
    get_api_call_limit,
    get_renewal_period,
    get_current_usage
)
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
        self.user_one = User.objects.create(email=self.email_one, id=1)
        self.user_two = User.objects.create(email=self.email_two, id=2)
        self.user_three = User.objects.create(email=self.email_three, id=3)
        self.yearly_renewal_period = 'YEARLY'
        self.monthly_renewal_period = 'MONTHLY'

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
            name="contributor three free",
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

        self.current_usage_one = 10
        self.current_usage_two = 2
        self.current_usage_three = -1

    def test_get_api_call_limit(self):
        period_limit_one = get_api_call_limit(self.contrib_one.id)
        period_limit_two = get_api_call_limit(self.contrib_two.id)
        self.assertEqual(
           str(self.limit_one.period_limit), period_limit_one
        )
        self.assertEqual(
                str(self.limit_two.period_limit), period_limit_two
        )

    def test_get_renewal_period(self):
        renewal_period_one = get_renewal_period(self.contrib_one.id)
        renewal_period_two = get_renewal_period(self.contrib_two.id)
        renewal_period_three = get_renewal_period(self.contrib_three.id)
        self.assertEqual(
            self.yearly_renewal_period, renewal_period_one
        )
        self.assertEqual(
            self.monthly_renewal_period, renewal_period_two
        )
        self.assertEqual(
            self.current_usage_three, renewal_period_three
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
        current_usage_one = get_current_usage(self.user_one.id)
        current_usage_two = get_current_usage(self.user_two.id)
        current_usage_three = get_current_usage(self.user_three.id)

        self.assertEqual(
            current_usage_one, str(self.current_usage_one)
        )
        self.assertEqual(
            current_usage_two, str(self.current_usage_two)
        )
        self.assertEqual(
            current_usage_three, '0'
        )
