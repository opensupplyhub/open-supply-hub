from api.models.facility.facility import Facility
import mercantile

from django.contrib.gis.geos import Polygon
from django.db import connection

GRID_ZOOM_FACTOR = 3


def get_facility_grid_vector_tile(params, layer, z, x, y):
    xy_bounds = mercantile.xy_bounds(x, y, z)

    hex_width = abs(xy_bounds.right - xy_bounds.left) / (2**GRID_ZOOM_FACTOR)
    # hex_grid_query = """
    #     CREATE TEMP TABLE hex_grid (geom, mvt_geom, wgs84_geom) AS (
    #       SELECT geom, ST_AsMVTGeom(
    #         ST_Centroid(geom), ST_MakeEnvelope(
    #             {xmin}, {ymin}, {xmax}, {ymax}
    #     )), ST_Transform (geom, 4326)
    #       FROM generate_hexgrid({width}, {xmin}, {ymin}, {xmax}, {ymax})
    #     )
    # """
    
    query = """
        SELECT ST_AsMVT(q, 'facilitygrid') from (
        SELECT ST_AsMVTGeom(
            ST_Centroid(geom), ST_MakeEnvelope(
            {xmin}, {ymin}, {xmax}, {ymax}
            )) as mvt_geom,
            count(location),
            ST_XMin(ST_Envelope(ST_Transform (geom, 4326))) as xmin,  
            ST_YMin(ST_Envelope(ST_Transform (geom, 4326))) as ymin,  
            ST_XMax(ST_Envelope(ST_Transform (geom, 4326))) as xmax,  
            ST_YMax(ST_Envelope(ST_Transform (geom, 4326))) as ymax
        FROM generate_hexgrid({width}, {xmin}, {ymin}, {xmax}, {ymax})
        JOIN api_facility ON ST_Contains(ST_Transform (geom, 4326), location)
        {where_clause}
        GROUP BY
            ST_AsMVTGeom(
            ST_Centroid(geom), ST_MakeEnvelope(
                {xmin}, {ymin}, {xmax}, {ymax}
            ))
            , ST_XMin(ST_Envelope(ST_Transform (geom, 4326)))
            , ST_YMin(ST_Envelope(ST_Transform (geom, 4326))) 
            , ST_XMax(ST_Envelope(ST_Transform (geom, 4326))) 
            , ST_YMax(ST_Envelope(ST_Transform (geom, 4326)))
            ) as q
    """

    location_query, location_params = (
        Facility.objects.filter_by_query_params(params)
        .values("location")
        .query.sql_with_params()
    )
    wrap_filter = (
        "ST_AsMVTGeom(ST_Centroid(geom), ST_MakeEnvelope("
        "   {xmin}, {ymin}, {xmax}, {ymax}"
        ")) is not null and "
        "abs("
        "   ST_XMax(ST_Envelope(ST_Transform (geom, 4326)))"
        " - ST_XMin(ST_Envelope(ST_Transform (geom, 4326)))"
        ") < 180".format(
            xmin=xy_bounds.left,
            ymin=xy_bounds.bottom,
            xmax=xy_bounds.right,
            ymax=xy_bounds.top
        )
    )
    if location_query.find("WHERE") >= 0:
        where_clause = location_query[
            location_query.find("WHERE"):
        ] + " AND {} ".format(wrap_filter)
    else:
        where_clause = " WHERE {} ".format(wrap_filter)

    query = query.format(
        width=hex_width,
        xmin=xy_bounds.left,
        ymin=xy_bounds.bottom,
        xmax=xy_bounds.right,
        ymax=xy_bounds.top,
        where_clause=where_clause
    )

    with connection.cursor() as cursor:
        cursor.execute(query, location_params)
        rows = cursor.fetchall()
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
    ns_buffer = (
        abs(tile_bounds.north - tile_bounds.south) * filter_buffer_percent
    )

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
        layer, query
    )

    with connection.cursor() as cursor:
        cursor.execute(st_asmvt_query, params_for_sql)
        rows = cursor.fetchall()
        return rows[0][0]
