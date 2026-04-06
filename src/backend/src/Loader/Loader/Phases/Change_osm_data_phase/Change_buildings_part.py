import psycopg2
import time
import math


def update_building_record_table(table, 
                                 cursor, 
                                 gid, 
                                 value, 
                                 levels):
    if levels > 0:
        cursor.execute(f"UPDATE {table}"
                       f" SET is_drawable = {value},"
                       f" building_levels = {math.ceil(levels)}"
                       f" WHERE id = {gid}")
    else:
        cursor.execute(f"UPDATE {table}"
                       f" SET is_drawable = {value}"
                       f" WHERE id = {gid}")


def update_building_part_record(table, 
                                cursor, 
                                gid, 
                                value, 
                                building_type):
    
    cursor.execute(f"UPDATE {table}"
                   f" SET is_drawable = {value},"
                   f" type = '{building_type}'"
                   f" WHERE id = {gid}")


def handle_multipart_buildings(conn):
    cursor = conn.cursor(name='buildings_fix_iterator')
    cursor.itersize = 1000
    cursorA = conn.cursor()

    count_fixed = 0

    cursor.execute(" SELECT"
                   "   id, building_levels, type, ST_Area(geometry), ST_AsText(geometry) "
                   " FROM osm_buildings_poly "
                   " WHERE (building_levels = 0 or building_levels is null or building_part = 'no'"
                   " or ST_GeometryType(geometry) = 'ST_MultiPolygon')"
                   " and ST_Area(geometry) > 2000.0")

    print("Изменение многосекционных зданий")

    for idx, rec in enumerate(cursor):
        if idx % 1000 == 0:
            print(idx)

        gid, levels, bld_type, area, geometry = rec

        cursorA.execute(f"SELECT id, building_levels, ST_Area(ST_Intersection(geometry, 'SRID=3857;{geometry}')) "
                        f" FROM osm_building_parts_poly "
                        f" WHERE ST_Intersects(geometry, 'SRID=3857;{geometry}')")

        total_area_inter = 0
        ids = []
        total_levels_weighted = 0
        total_area_inter_weighted = 0

        for row in cursorA.fetchall():
            pid, plevels, area_inter = row
            total_area_inter += area_inter

            if plevels is not None:
                total_levels_weighted += plevels * area_inter
                total_area_inter_weighted += area_inter

            ids.append(pid)

        if total_area_inter_weighted/area < 0.8 and levels != 0:
            continue

        total_levels_weighted = total_levels_weighted / total_area_inter
        if levels is not None and levels > 0:
            total_levels_weighted = 0
        update_building_record_table("osm_buildings_poly", cursorA, gid, -1, total_levels_weighted)

        for pid in ids:
            update_building_part_record("osm_building_parts_poly", cursorA, pid, 1, bld_type)

        count_fixed += 1

    conn.commit()
    print(f"Измененно {count_fixed} зданий.")


def handle_industrial_buildings(conn):
    print("Начало обновнления таблиц зданий.")

    cursor = conn.cursor(name='industrial_poly_cursor')

    cursor.itersize = 1000
    cursorA = conn.cursor()

    cursor.execute(" SELECT osm_buildings_poly.id, osm_industrial_zones.type from osm_buildings_poly"
                   " JOIN osm_industrial_zones on"
                   " ST_Intersects(osm_industrial_zones.geometry, osm_buildings_poly.geometry)"
                   " WHERE osm_buildings_poly.type = 'yes';")

    i = 0
    for row in cursor.fetchall():
        zid, ztype = row
        cursorA.execute(f"UPDATE osm_buildings_poly SET type = '{ztype}' WHERE id = {zid}")
        i += 1
        if i % 1000 == 0:
            print(i)

    conn.commit()
    print(f"Обновление закончено {i} зданий.")


def change_buildings(database_url: str):
    conn = psycopg2.connect(database_url)
    print("Connected to db")
    tic = time.perf_counter()

    handle_industrial_buildings(conn)

    handle_multipart_buildings(conn)

    conn.commit()

    if conn:
        conn.close()

    toc = time.perf_counter()
    print(f"Закончено изменение зданий{toc - tic:0.1f} s")

