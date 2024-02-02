from api.limits import check_api_limits, get_end_of_year
from api.models import (
    ApiBlock,
    ApiLimit,
    Contributor,
    ContributorNotifications,
    RequestLog,
    User,
)
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone


class ApiLimitTest(TestCase):
    def setUp(self):
        self.email_one = "one@example.com"
        self.email_two = "two@example.com"
        self.user_one = User.objects.create(email=self.email_one)
        self.user_two = User.objects.create(email=self.email_two)

        self.contrib_one = Contributor.objects.create(
            admin=self.user_one,
            name="contributor one",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contrib_two = Contributor.objects.create(
            admin=self.user_two,
            name="contributor two",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        now = timezone.now()
        self.limit_one = ApiLimit.objects.create(
            contributor=self.contrib_one,
            yearly_limit=10,
            period_start_date=now,
        )

        self.limit_two = ApiLimit.objects.create(
            contributor=self.contrib_two,
            yearly_limit=10,
            period_start_date=now,
        )

        self.notification_time = timezone.now()
        self.notification = ContributorNotifications.objects.create(
            contributor=self.contrib_two,
            api_limit_warning_sent_on=self.notification_time,
            api_limit_exceeded_sent_on=self.notification_time,
            api_grace_limit_exceeded_sent_on=self.notification_time,
        )

    def test_under_limit_does_nothing(self):
        check_api_limits(timezone.now())
        self.assertEqual(
            ApiBlock.objects.filter(contributor=self.contrib_one).count(), 0
        )

    def test_limit_only_applies_within_period(self):
        last_month = timezone.now() - relativedelta(months=1)
        for x in range(10):
            r = RequestLog.objects.create(
                user=self.user_one, response_code=200
            )
            r.created_at = last_month
            r.save()

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(contributor=self.contrib_one).count(), 0
        )

        warning = ContributorNotifications.objects.get(
            contributor=self.contrib_one
        )
        self.assertIsNone(warning.api_limit_warning_sent_on)

    def test_limit_warning_sent_once(self):
        for x in range(10):
            RequestLog.objects.create(user=self.user_one, response_code=200)
            RequestLog.objects.create(user=self.user_two, response_code=200)

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(contributor=self.contrib_one).count(), 0
        )
        self.assertEqual(
            ApiBlock.objects.filter(contributor=self.contrib_two).count(), 0
        )

        warning = ContributorNotifications.objects.get(
            contributor=self.contrib_one
        )
        self.assertIsNotNone(warning.api_limit_warning_sent_on)

        warning_two = ContributorNotifications.objects.get(
            contributor=self.contrib_two
        )
        self.assertEqual(
            warning_two.api_limit_warning_sent_on, self.notification_time
        )

    def test_over_limit_block_set_once(self):
        ApiBlock.objects.create(
            contributor=self.contrib_two,
            until=get_end_of_year(self.notification_time),
            active=False,
            limit=10,
            actual=11,
        )

        for x in range(11):
            RequestLog.objects.create(user=self.user_one, response_code=200)
            RequestLog.objects.create(user=self.user_two, response_code=200)

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(contributor=self.contrib_one).count(), 1
        )
        self.assertEqual(
            ApiBlock.objects.filter(contributor=self.contrib_two).count(), 1
        )

        notice = ContributorNotifications.objects.get(
            contributor=self.contrib_one
        )
        self.assertIsNotNone(notice.api_limit_exceeded_sent_on)

        notice_two = ContributorNotifications.objects.get(
            contributor=self.contrib_two
        )
        self.assertEqual(
            notice_two.api_limit_exceeded_sent_on, self.notification_time
        )
