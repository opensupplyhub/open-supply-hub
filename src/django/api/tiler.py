from api.models.facility.facility import Facility
from api.models.facility.facility_index import FacilityIndex
import mercantile

from django.contrib.gis.geos import Polygon
from django.db import connection

GRID_ZOOM_FACTOR = 3
HI_LIMIT = 100


def get_facility_grid_vector_tile(params, layer, z, x, y):
    xy_bounds = mercantile.xy_bounds(x, y, z)
    hex_width = abs(xy_bounds.right - xy_bounds.left) / (2**GRID_ZOOM_FACTOR)

    query = """
    SELECT ST_AsMVT(q, 'facilitygrid') FROM (
        SELECT ST_AsMVTGeom(
            ST_Centroid(geom),
            ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax})
        ) AS mvt_geom,
        (SELECT COUNT(*) FROM (
            SELECT * FROM api_facilityindex
            WHERE
                ST_Contains(ST_Transform(geom, 4326), location)
                AND ({where_clause})
            LIMIT {limit}
            ) as ss
        ) as count,
        ST_XMin(ST_Envelope(ST_Transform(geom, 4326))) AS xmin,
        ST_YMin(ST_Envelope(ST_Transform(geom, 4326))) AS ymin,
        ST_XMax(ST_Envelope(ST_Transform(geom, 4326))) AS xmax,
        ST_YMax(ST_Envelope(ST_Transform(geom, 4326))) AS ymax
    FROM
        generate_hexgrid({width}, {xmin}, {ymin}, {xmax}, {ymax})
    WHERE
        ST_AsMVTGeom(
            ST_Centroid(geom),
            ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax})
        ) IS NOT NULL
        AND ABS(ST_XMax(ST_Envelope(ST_Transform(geom, 4326))) -
            ST_XMin(ST_Envelope(ST_Transform(geom, 4326)))) < 180
            AND exists (
            SELECT 1 FROM api_facilityindex
            WHERE
                ST_Contains(ST_Transform(geom, 4326), location)
                AND ({where_clause})
        )
    ) AS q;
    """

    location_query, location_params = (
        FacilityIndex.objects.filter_by_query_params(params)
        .query.sql_with_params()
    )
    where_clause = "TRUE"

    if location_query.find("WHERE") >= 0:
        where_clause = location_query[
            location_query.find("WHERE")+len("WHERE"):
        ]

    query = query.format(
        width=hex_width,
        xmin=xy_bounds.left,
        ymin=xy_bounds.bottom,
        xmax=xy_bounds.right,
        ymax=xy_bounds.top,
        where_clause=where_clause,
        limit=HI_LIMIT
    )

    with connection.cursor() as cursor:
        cursor.execute(query, location_params+location_params)
        rows = cursor.fetchall()
        if len(rows) == 0 or len(rows[0]) == 0:
            return None
        return rows[0][0]


def get_facilities_vector_tile(params, layer, z, x, y):
    """
    Create a vector tile for a layer generated via PostGIS's `ST_AsMVT`
    function, filtered by params.

    Arguments:
    params (dict) -- Request query parameters whose potential choices are
                     enumerated in `api.constants.FacilitiesQueryParams`
    layer (string) -- The name of the tile layer. Currently only "facilities"
                      is supported.
    z (int) -- Zoom level.
    x (int) -- X (horizontal) position for requested tile on a grid.
    y (int) -- Y (vertical) position for requested tile on a grid.

    Returns:
    A vector tile.
    """
    tile_bounds = mercantile.bounds(x, y, z)

    mvt_geom_query = """
        ST_AsMVTGeom(
            location,
            ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}, 4326),
            4096,
            1024,
            true
        ) """

    filter_buffer_percent = 0.2
    ew_buffer = abs(tile_bounds.east - tile_bounds.west) * \
        filter_buffer_percent
    ns_buffer = abs(tile_bounds.north - tile_bounds.south) * \
        filter_buffer_percent

    filter_polygon = Polygon.from_bbox(
        (
            tile_bounds.west - ew_buffer,
            tile_bounds.south - ns_buffer,
            tile_bounds.east + ew_buffer,
            tile_bounds.north + ns_buffer,
        )
    )

    query, params_for_sql = (
        Facility.objects.filter_by_query_params(params)
        .filter(location__within=filter_polygon)
        .extra(
            select={
                "location": mvt_geom_query.format(
                    xmin=tile_bounds.west,
                    ymin=tile_bounds.south,
                    xmax=tile_bounds.east,
                    ymax=tile_bounds.north,
                ),
                "x": x,
                "y": y,
                "z": z,
            }
        )
        .values("location", "id", "name", "address", "x", "y", "z")
        .query.sql_with_params()
    )

    st_asmvt_query = "SELECT ST_AsMVT(q, '{}') FROM ({}) AS q".format(
        layer, query)

    with connection.cursor() as cursor:
        cursor.execute(st_asmvt_query, params_for_sql)
        rows = cursor.fetchall()
        return rows[0][0]
