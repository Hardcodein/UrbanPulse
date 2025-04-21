from Loader.Phases.Human_density_coverage.Helpers_human_density import get_line_width_and_default_lanes


def get_area_roads(conn, cursorQ, area_land_text, coef):
    table = "osm_roads_way"

    cursorQ.execute(f"SELECT id,"
                    f"   ST_Length(ST_Intersection(geometry, 'SRID=3857;{area_land_text}')) as intersection,"
                    f"   type,"
                    f"   lanes"
                    f" FROM {table}"
                    f" WHERE"
                    f" type != 'service' and ST_Intersects(geometry, 'SRID=3857;{area_land_text}')")

    area_roads = 0.0

    for recI in cursorQ.fetchall():
        gid, length, highway, lanes = recI
        lane_width, def_lanes_count = get_line_width_and_default_lanes(highway)
        lanes_count = lanes if lanes is not None and lanes > 0 else def_lanes_count
        area_roads += length * (lane_width * coef) * lanes_count

    return area_roads


def get_rail_width():
    return 1.5


def get_area_rails(conn, cursorQ, area_land_text, coef):
    table = "osm_railways_way"

    cursorQ.execute(f"SELECT id,"
                    f"   ST_Length(ST_Intersection(geometry, 'SRID=3857;{area_land_text}')) as intersection"
                    f" FROM {table}"
                    f" WHERE"
                    f" ST_Intersects(geometry, 'SRID=3857;{area_land_text}')")

    area_rails = 0.0

    for recI in cursorQ.fetchall():
        gid, length = recI
        rail_width = get_rail_width() * coef
        area_rails += length * rail_width

    return area_rails


def get_area_water(cursorQ, area_land_text):
    table = "osm_natural_water_poly"

    cursorQ.execute(f"SELECT id,"
                    f"   ST_Area(ST_Intersection(geometry, 'SRID=3857;{area_land_text}')) as intersection"
                    f" FROM {table}"
                    f" WHERE"
                    f"   tunnel != 'yes' and "
                    f" ST_Intersects(geometry, 'SRID=3857;{area_land_text}')")

    area_water = 0.0

    for recI in cursorQ.fetchall():
        gid, area = recI
        area_water += area

    return area_water
