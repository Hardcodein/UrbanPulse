import psycopg2
import json
import time


import useful as u

def coords_from_text(text):
    obj = json.loads(text)
    if obj["type"] in ['Point', 'LineString']:
        return obj["coordinates"]

    return obj["coordinates"][0]


def get_area_buildings(conn, cursorQ, area_land_text):
    table = "osm_buildings_poly"

    cursorQ.execute(f"SELECT id,"
                    f"   ST_Area(ST_Intersection(geometry, 'SRID=3857;{area_land_text}')),"
                    "    building_levels,"
                    "    min_level"
                    f" FROM {table}"
                    f" WHERE"
                    f"   ST_Intersects(geometry, 'SRID=3857;{area_land_text}')")

    area_bld = 0.0
    area_bld_levels = 0.0

    bld_count_no_levels = 0
    bld_count_levels = 0.0
    levels_sum = 0

    for recI in cursorQ.fetchall():
        gid, inter_area, levels, min_level = recI

        multiplier = 0.0
        if levels is not None:
            multiplier = levels

            if min_level is not None and 0 < min_level < levels:
                multiplier -= min_level

            levels_sum += multiplier
            bld_count_levels += 1
        else:
            bld_count_no_levels += 1

        area_bld_levels += inter_area * multiplier

        if bld_count_no_levels > 0 and bld_count_levels > 0:
            area_bld_levels += (levels_sum / bld_count_levels) * bld_count_no_levels

        area_bld += inter_area

    return area_bld, area_bld_levels


def get_line_width_and_default_lanes(highway):
    if highway in ["motorway", "motorway_link", "trunk", "trunk_link"]:
        return 3.75, 4

    if highway in ["primary", "primary_link", "secondary", "secondary_link"]:
        return 3.5, 4

    if highway in ["tertiary", "tertiary_link", "street", "living_street"]:
        return 3.5, 3

    if highway in ["road"]:
        return 3.0, 2

    return 2.75, 2


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


def update_building_record(cursorQ, gid, pct, pct_dens):
    cursorQ.execute(f"UPDATE osm_buildings_poly"
                    f" SET pct_building = {pct},"
                    f" pct_dens_building = {pct_dens}"
                    f" WHERE id = {gid}")


def update_building_parts_records(conn, gid, pct, pct_dens):
    cursorN = conn.cursor()
    cursorM = conn.cursor()
    cursorN.execute(f"SELECT ST_AsText(geometry) from osm_buildings_poly where id = {gid}");
    geom_text = cursorN.fetchone()[0]

    cursorN.execute(f"SELECT id "
                    f" FROM osm_building_parts_poly "
                    f" WHERE is_drawable = 1 and ST_Intersects(geometry, 'SRID=3857;{geom_text}')")

    for row in cursorN.fetchall():
        pid = row[0]
        cursorM.execute(f"UPDATE osm_building_parts_poly"
                        f" SET pct_building = {pct},"
                        f" pct_dens_building = {pct_dens}"
                        f" WHERE id = {pid}")


def calc_and_update_pct(conn):
    cursor = conn.cursor(name='buildings_iterator')
    cursor.itersize = 100
    cursorA = conn.cursor()

    cursor.execute(f" SELECT"
                   f"   id, building_levels, is_drawable, ST_AsGeoJSON(buffer), ST_AsText(buffer), ST_Area(buffer),"
                   f"   coef"
                   f" FROM"
                   f"   (SELECT"
                   f"       id, building_levels, is_drawable, geometry, coef, "
                   f"       ST_Buffer(geometry, {u.NEIGHBOURS_DIST_M} * coef) as buffer"
                   f"    FROM "
                   f" (SELECT id, building_levels, is_drawable, geometry, {u.QUERY_COEF} as coef FROM"
                   f" osm_buildings_poly) as q_inner) as q")
    # where id = 46657131 26622966 37446040 39537474

    print("Fetching buildings geometry: retrieved the cursor")

    for idx, rec in enumerate(cursor):
        gid, levels_count, is_drawable, buffer_text, buffer_plaintext, buffer_area, coef = rec
        if buffer_area is None or buffer_area <= 0:
            continue
        buffer = coords_from_text(buffer_text)

        area_total = buffer_area
        area_roads = get_area_roads(conn, cursorA, buffer_plaintext, coef) + \
                     get_area_rails(conn, cursorA, buffer_plaintext, coef)
        area_water = get_area_water(cursorA, buffer_plaintext)

        area_bld, area_bld_levels = get_area_buildings(conn, cursorA, buffer_plaintext)

        if area_bld > area_total or area_roads + area_water > area_total or area_total - area_roads - area_water < area_bld \
                or area_total == 0.0 or area_bld == 0.0:
            print(f"ERROR IN AREA CALCULATION:"
                  f"id = {gid}, "
                  f"area land = {area_total}, "
                  f"area buildings = {area_bld}, "
                  f"area roads = {area_roads}, "
                  f"area water = {area_water}")
            continue

        #print(f"Area land: {area_total}, area roads: {area_roads}, area buildings: {area_bld}")
        area_total -= area_roads
        area_total -= area_water

        pct = area_bld / area_total * 100.0
        pct_dens = area_bld_levels / area_total * 100.0
        if levels_count is None or levels_count < 1:
            pct_dens = 0.0

        # print(gid, pct, pct_dens)

        if idx % 1000 == 0:
            print("Calc bld pct:", idx)

        #print(f"Pct bld: {pct}, pct density bld: {pct_dens}")
        update_building_record(cursorA, gid, pct, pct_dens)

        if is_drawable is not None:
            update_building_parts_records(conn, gid, pct, pct_dens)

    conn.commit()


def generalize_hex_tables(conn):
    cursor_s = conn.cursor()

    for suffix in ["", "_s", "_m", "_l", "_xl"]:
        gen_table = "hex_tiles" + suffix
        print(f"Started filling {gen_table} table")
        cursor = conn.cursor(name=f'hex_iterator_{gen_table}')
        cursor.itersize = 500
        cursor.execute(f"SELECT gid, ST_AsText(geometry) FROM {gen_table}")

        for i, row in enumerate(cursor.fetchall()):
            gid, geom = row

            cursor_s.execute(f" SELECT pct_building, pct_dens_building, "
                             f" ST_Area(ST_Intersection(geometry, 'SRID=3857;{geom}'))"
                             f" FROM osm_buildings_poly WHERE"
                             f" ST_Intersects(geometry, 'SRID=3857;{geom}')")

            gen_pct_bld = 0.0
            area_pct = 0.0
            gen_pct_dens_bld = 0.0
            area_pct_dens = 0.0

            for row_i in cursor_s.fetchall():
                pct_bld, pct_dens_bld, area_bld = row_i
                if pct_bld is not None and pct_bld > 0.0:
                    gen_pct_bld += float(pct_bld) * area_bld
                    area_pct += area_bld
                if pct_dens_bld is not None and pct_dens_bld > 0.0:
                    gen_pct_dens_bld += float(pct_dens_bld) * area_bld
                    area_pct_dens += area_bld

            if gen_pct_bld > 0:
                gen_pct_bld = gen_pct_bld / area_pct
            if gen_pct_dens_bld > 0:
                gen_pct_dens_bld = gen_pct_dens_bld / area_pct_dens

            if i % 1000 == 0:
                print(f"{gen_table}, {i}")

            cursor_s.execute(f"UPDATE {gen_table} SET bld_pct = {gen_pct_bld}, "
                             f"bld_dens_pct = {gen_pct_dens_bld} WHERE gid = {gid}")

        conn.commit()


def calc_density(database_url: str):
    conn = psycopg2.connect(database_url)
    print("Подклюючение к БД")
    tic = time.perf_counter()

    #calc_and_update_pct(conn)

    generalize_hex_tables(conn)

    if conn:
        conn.close()

    toc = time.perf_counter()

    print(f"Finished calculating constructions density in {toc - tic:0.1f} s")


if __name__ == "__main__":
    calc_density()
