from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from django.db.models import F
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.aggregates.general import ArrayAgg

from api.models import (Contributor, RequestLog, ContributorNotifications,
                        ApiLimit, ApiBlock)
from api.mail import (send_api_notice, send_admin_api_notice, send_api_warning,
                      send_admin_api_warning)

LAST_MONTH_OF_THE_YEAR = 12
MINIMUM_DAY_TO_ROUND = 28


def get_end_of_year(at_datetime):
    return datetime.combine(at_datetime.replace(month=12, day=31), time.max,
                            at_datetime.tzinfo)


def round_start_date(date: datetime):
    start_date = date
    if start_date.month == LAST_MONTH_OF_THE_YEAR:
        start_date = start_date.replace(day=1,
                                        month=1,
                                        year=start_date.year + 1)
    else:
        start_date = start_date.replace(day=1,
                                        month=start_date.month + 1)

    return start_date


def get_start_date(period_start_date: datetime, renewal_period):
    utc = timezone.utc
    start_date = period_start_date
    if start_date.day > MINIMUM_DAY_TO_ROUND:
        start_date = round_start_date(start_date)
    if renewal_period == 'MONTHLY':
        one_month_in_past = datetime.now(tz=utc) - relativedelta(months=1)
        while (start_date < one_month_in_past):
            start_date = start_date + relativedelta(months=1)
        return start_date
    if renewal_period == 'YEARLY':
        one_year_in_past = datetime.now(tz=utc) - relativedelta(years=1)
        while (start_date < one_year_in_past):
            start_date = start_date + relativedelta(years=1)
        return start_date

    return start_date


def get_api_block(contributor):
    return ApiBlock.objects.filter(
                contributor=contributor).order_by('-until').first()


def create_api_block(contributor, limit, actual, start_date, renewal_period):
    if renewal_period is None or renewal_period == 'YEARLY':
        until = start_date + relativedelta(years=1)
    else:
        until = start_date + relativedelta(months=1)

    ApiBlock.objects.create(contributor=contributor,
                            until=until, active=True,
                            limit=limit, actual=actual)


def update_api_block(apiBlock: ApiBlock,
                     limit,
                     request_count,
                     is_active):
    with transaction.atomic():
        apiBlock.limit = limit
        apiBlock.actual = request_count
        apiBlock.active = is_active
        apiBlock.save()


def block_free_api_contributor(contributor,
                               limit,
                               request_count,
                               start_date,
                               at_datetime):
    apiBlock = get_api_block(contributor)
    actual_limit = request_count if limit is None else limit
    # If there is no current API block
    if apiBlock is None or apiBlock.until < at_datetime:
        create_api_block(contributor,
                         actual_limit,
                         request_count,
                         start_date,
                         None)
    else:
        if apiBlock.active:
            return
        if (apiBlock.grace_limit is None or
                request_count > apiBlock.grace_limit):
            update_api_block(apiBlock,
                             actual_limit,
                             request_count,
                             is_active=True)


@transaction.atomic
def check_contributor_api_limit(at_datetime, c):
    try:
        contributor = Contributor.objects.get(id=c.get('contributor'))
    except Contributor.DoesNotExist:
        # API Limits and Blocks are linked to contributors.
        # Users without contributors are blocked from the system
        # in middleware and don't need to be handled here.
        return
    log_dates = c.get('log_dates')
    notification, created = ContributorNotifications \
        .objects \
        .get_or_create(contributor=contributor)
    try:
        apiLimit = ApiLimit.objects.get(contributor=contributor)
        limit = apiLimit.period_limit
        renewal_period = apiLimit.renewal_period
        start_date = get_start_date(apiLimit.period_start_date, renewal_period)
    except ObjectDoesNotExist:
        limit = None
        start_date = get_start_date(min(log_dates), None)

    logs_for_period = [x for x in log_dates if x >= start_date]
    request_count = len(logs_for_period)
    if (limit is None or
            renewal_period == ''):
        block_free_api_contributor(contributor,
                                   limit,
                                   request_count,
                                   start_date,
                                   at_datetime)
        return

    apiBlock = get_api_block(contributor)
    if limit == 0:
        if (apiBlock is not None and
            apiBlock.active and
                apiBlock.until > at_datetime):
            update_api_block(apiBlock, limit, request_count, is_active=False)
        return
    if request_count > (limit * .9) and request_count <= limit:
        warning_sent = notification.api_limit_warning_sent_on
        # If no warning was sent in this period
        if (warning_sent is None or warning_sent < start_date):
            send_api_warning(contributor, limit)
            send_admin_api_warning(contributor.name, limit)
            notification.api_limit_warning_sent_on = at_datetime
            notification.save()
    if request_count > limit:
        # If there is no current API block
        if apiBlock is None or apiBlock.until < at_datetime:
            create_api_block(contributor,
                             limit,
                             request_count,
                             start_date,
                             renewal_period)
            exceeded_sent = notification.api_limit_exceeded_sent_on
            if (exceeded_sent is None or
                    exceeded_sent.month < at_datetime.month):
                send_api_notice(contributor, limit)
                send_admin_api_notice(contributor.name, limit)
                notification.api_limit_exceeded_sent_on = (
                    at_datetime)
                notification.save()
        else:
            if apiBlock.active:
                return
            if apiBlock.active is False and apiBlock.grace_limit is None:
                update_api_block(apiBlock,
                                 limit,
                                 request_count,
                                 is_active=True)
                return
            grace_limit = apiBlock.grace_limit
            if request_count > grace_limit:
                update_api_block(apiBlock,
                                 limit,
                                 request_count,
                                 is_active=True)
                send_api_notice(contributor, limit, grace_limit)
                send_admin_api_notice(contributor.name, limit, grace_limit)
                notification.api_grace_limit_exceeded_sent_on = (
                    at_datetime)
                notification.save()
    else:
        if apiBlock is not None and apiBlock.active:
            update_api_block(apiBlock, limit, request_count, is_active=False)


def check_api_limits(at_datetime):
    contributor_logs = RequestLog.objects.filter(
            response_code__gte=200,
            response_code__lte=299).annotate(
                contributor=F('user__contributor__id')
            ).values('contributor').annotate(
                log_dates=ArrayAgg('created_at')
            )
    for c in contributor_logs:
        check_contributor_api_limit(at_datetime, c)
