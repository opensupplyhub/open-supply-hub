from django.db.models import F
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.aggregates.general import ArrayAgg

from api.models import (Contributor, RequestLog, ContributorNotifications,
                        ApiLimit, ApiBlock)
from api.mail import (send_api_notice, send_admin_api_notice, send_api_warning,
                      send_admin_api_warning)
from api.limitation.date.date_limitation_context import (
    DateLimitationContext
)
from api.limitation.date.blank_date_limitation import (
    BlankDateLimitation
)
from api.limitation.date.monthly_date_limitation import (
    MonthlyDateLimitation
)
from api.limitation.date.yearly_date_limitation import (
    YearlyDateLimitation
)


def get_api_block(contributor):
    return ApiBlock.objects.filter(
                contributor=contributor).order_by('-until').first()


def create_api_block(contributor, limit, actual, until):
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
                               until,
                               at_datetime):
    apiBlock = get_api_block(contributor)
    actual_limit = request_count if limit is None else limit
    # If there is no current API block
    if apiBlock is None or apiBlock.until < at_datetime:
        create_api_block(contributor,
                         actual_limit,
                         request_count,
                         until)
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
        date = apiLimit.period_start_date
    except ObjectDoesNotExist:
        limit = None
        renewal_period = ''
        date = min(log_dates)

    context = DateLimitationContext()

    if renewal_period is '':
        context.setStrategy(BlankDateLimitation())
    if renewal_period == 'MONTHLY':
        context.setStrategy(MonthlyDateLimitation())
    if renewal_period == 'YEARLY':
        context.setStrategy(YearlyDateLimitation())

    date_limitation = context.execute(date)
    start_date = date_limitation.get_start_date()
    until = date_limitation.get_api_block_until()

    logs_for_period = [x for x in log_dates if x >= start_date]
    request_count = len(logs_for_period)

    if (limit is None or
            renewal_period == ''):
        block_free_api_contributor(contributor,
                                   limit,
                                   request_count,
                                   until,
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
                             until)
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
            update_api_block(apiBlock,
                             limit,
                             request_count,
                             is_active=False)


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
