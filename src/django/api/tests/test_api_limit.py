from api.limits import check_api_limits
from api.models import (
    ApiBlock,
    ApiLimit,
    Contributor,
    ContributorNotifications,
    RequestLog,
    User,
)
from api.limitation.date.date_limitation_context import (
    DateLimitationContext
)
from api.limitation.date.blank_date_limitation import (
    BlankDateLimitation
)
from dateutil.relativedelta import relativedelta
from datetime import datetime, time

from django.test import TestCase
from django.utils import timezone


class ApiLimitTest(TestCase):
    def setUp(self):
        self.email_one = "one@example.com"
        self.email_two = "two@example.com"
        self.email_three_free = "three.free@example.com"
        self.user_one = User.objects.create(email=self.email_one)
        self.user_two = User.objects.create(email=self.email_two)
        self.user_three_free = User.objects.create(email=self.email_three_free)

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
        self.contrib_three_free = Contributor.objects.create(
            admin=self.user_three_free,
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
            period_limit=10,
            period_start_date=now,
            renewal_period=ApiLimit.YEARLY,
        )

        self.notification_time = timezone.now()
        self.notification = ContributorNotifications.objects.create(
            contributor=self.contrib_two,
            api_limit_warning_sent_on=self.notification_time,
            api_limit_exceeded_sent_on=self.notification_time,
            api_grace_limit_exceeded_sent_on=self.notification_time,
        )

    def get_end_of_year(self, at_datetime: datetime):
        return datetime.combine(at_datetime.replace(month=12, day=31),
                                time.max,
                                at_datetime.tzinfo)

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
            until=self.get_end_of_year(self.notification_time),
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

    def test_free_user_block_create(self):
        RequestLog.objects.create(user=self.user_three_free, response_code=200)

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

    def test_free_user_block_activate(self):
        ApiBlock.objects.create(
            contributor=self.contrib_three_free,
            until=self.get_end_of_year(self.notification_time),
            active=False,
            limit=1,
            actual=1,
        )

        RequestLog.objects.create(user=self.user_three_free, response_code=200)

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, True
        )

    def test_free_user_become_unlimited(self):
        ApiBlock.objects.create(
            contributor=self.contrib_three_free,
            until=self.get_end_of_year(self.notification_time),
            active=False,
            limit=1,
            actual=1,
        )

        RequestLog.objects.create(user=self.user_three_free, response_code=200)

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, True
        )

        ApiLimit.objects.create(
            contributor=self.contrib_three_free,
            period_limit=0,
            period_start_date=timezone.now(),
            renewal_period=ApiLimit.YEARLY,
        )

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, False
        )

    def test_free_user_become_paid(self):
        ApiBlock.objects.create(
            contributor=self.contrib_three_free,
            until=self.get_end_of_year(self.notification_time),
            active=False,
            limit=1,
            actual=1,
        )

        RequestLog.objects.create(user=self.user_three_free, response_code=200)

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, True
        )

        ApiLimit.objects.create(
            contributor=self.contrib_three_free,
            period_limit=500,
            period_start_date=timezone.now(),
            renewal_period=ApiLimit.YEARLY,
        )

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, False
        )

    def test_api_limit_blank_renewal_period(self):
        RequestLog.objects.create(user=self.user_three_free,
                                  response_code=200)

        ApiLimit.objects.create(
            contributor=self.contrib_three_free,
            period_limit=500,
            period_start_date=timezone.now(),
        )

        check_api_limits(timezone.now())

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, True
        )

    def test_api_limit_monthly_renewal_period(self):
        now = timezone.now()

        r_log_one = RequestLog.objects.create(user=self.user_three_free,
                                              response_code=200)
        r_log_two = RequestLog.objects.create(user=self.user_three_free,
                                              response_code=200)

        ApiLimit.objects.create(
            contributor=self.contrib_three_free,
            period_limit=1,
            period_start_date=now,
            renewal_period=ApiLimit.MONTHLY,
        )

        check_api_limits(now)

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, True
        )

        r_log_one.created_at = now - relativedelta(months=1)
        r_log_one.save()

        r_log_two.created_at = now - relativedelta(months=1)
        r_log_two.save()

        check_api_limits(now)

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, False
        )

    def test_api_limit_yearly_renewal_period(self):
        now = timezone.now()

        r_log_one = RequestLog.objects.create(user=self.user_three_free,
                                              response_code=200)
        r_log_two = RequestLog.objects.create(user=self.user_three_free,
                                              response_code=200)

        ApiLimit.objects.create(
            contributor=self.contrib_three_free,
            period_limit=1,
            period_start_date=now,
            renewal_period=ApiLimit.YEARLY,
        )

        check_api_limits(now)

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, True
        )

        r_log_one.created_at = now - relativedelta(years=1)
        r_log_one.save()

        r_log_two.created_at = now - relativedelta(years=1)
        r_log_two.save()

        check_api_limits(now)

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).count(), 1
        )

        self.assertEqual(
            ApiBlock.objects.filter(
                contributor=self.contrib_three_free
            ).first().active, False
        )

    def test_prepare_start_date(self):
        date_one = datetime(day=30, month=10, year=2024)
        context_one = DateLimitationContext()
        context_one.set_strategy(BlankDateLimitation())
        dateLimitation_one = context_one.execute(date_one)
        result_date_one = dateLimitation_one.get_start_date()

        self.assertEqual(
            result_date_one,
            datetime(day=1, month=11, year=2024)
        )

        date_two = datetime(day=29, month=12, year=2024)
        context_two = DateLimitationContext()
        context_two.set_strategy(BlankDateLimitation())
        dateLimitation_two = context_two.execute(date_two)
        result_date_two = dateLimitation_two.get_start_date()

        self.assertEqual(
            result_date_two,
            datetime(day=1, month=1, year=2025)
        )
