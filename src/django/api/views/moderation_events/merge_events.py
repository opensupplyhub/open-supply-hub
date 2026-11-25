from typing import Callable
from datetime import date

from django.db import connection

from ...serializers import MergeQueryParamsSerializer


def retrieve_merge_events(query: str,
                          fetcher: Callable[[object], list],
                          query_params: list = None) -> list:
    with connection.cursor() as cursor:
        cursor.execute(query, query_params)
        events = fetcher(cursor)

    return events


def fetch_all(cursor: object) -> list:
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """

    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def build_query_string(params: MergeQueryParamsSerializer) -> str:
    """
    Build a query string for retrieving merge events depending on the passed
    query parameters by API user.
    """

    query = (
        "SELECT afa.facility_id AS current_id, "
        "afa.os_id AS original_id, "
        "ahf.created_at, "
        "ahf.history_date AS merge_date"
        "{detail_fields}"
        "{source_data_sql}"
        "WHERE ahf.history_change_reason LIKE 'Merged with%%'"
        "{date_range}")

    date_gte = params.validated_data['date_greater_than_or_equal']
    date_lt = params.validated_data['date_less_than']
    contributors = params.validated_data['contributors']
    detail = params.validated_data['detail']

    detail_fields = generate_detail_fields(detail)
    source_data_sql = generate_source_data_sql(contributors)
    date_range = generate_date_range(date_gte, date_lt)

    query_params = list(contributors or [])
    query_params += [d.isoformat() for d in (date_gte, date_lt) if d]

    return query.format(detail_fields=detail_fields,
                        source_data_sql=source_data_sql,
                        date_range=date_range), query_params


def generate_detail_fields(detail: bool) -> str:
    return detail and (", ahf.name AS original_name, "
                       "ahf.address AS original_address") or ""


def generate_source_data_sql(contributors: list) -> str:
    if not contributors:
        return (" FROM api_historicalfacility ahf "
                "JOIN api_facilityalias afa ON afa.os_id = ahf.id ")

    return (f" FROM UNNEST(ARRAY[{', '.join(['%s'] * len(contributors))}]) "
            "as cid JOIN api_source asrc ON asrc.contributor_id = cid "
            "JOIN api_facilitylistitem afli ON afli.source_id = asrc.id "
            "JOIN api_historicalfacility ahf "
            "ON ahf.created_from_id = afli.id "
            "JOIN api_facilityalias afa ON afa.os_id = ahf.id ")


def generate_date_range(date_gte: date, date_lt: date) -> str:
    if date_gte and date_lt:
        return (" AND ahf.history_date >= %s "
                "AND ahf.history_date < %s")

    if date_gte:
        return " AND ahf.history_date >= %s"

    if date_lt:
        return " AND ahf.history_date < %s"

    return ""
