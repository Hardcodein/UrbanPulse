import time
from pathlib import Path

import psycopg2

tables = ["osm_subway_stations", "osm_subway_station_entrances"]

supported_cities = "'Москва', 'Челябинск', 'Тюмень', 'Санкт-Петербург', 'Архангельск', 'Алматы', 'Екатеринбург', " \
                   "'Самара', 'Краснодар', 'Сочи', 'Казань', 'Новосибирск','Ростов-на-Дону' "

def prepare_name(s):
    s = s.lower().strip()
    return s


def update_subways(conn):
    for table in tables:
        cursor = conn.cursor()
        cursor_find = conn.cursor()
        cursor_upd = conn.cursor()

        cursor.execute(f"SELECT id, ST_AsText(geometry) from {table}")
        for row in cursor.fetchall():
            gid, subway_geom = row
            cursor_find.execute(f"SELECT name FROM world_cities WHERE "
                                f"name_ru in ({supported_cities}) "
                                f"ORDER BY ST_Distance(geometry, 'SRID=3857;{subway_geom}') LIMIT 1")

            name = prepare_name(cursor_find.fetchone()[0])
            cursor_upd.execute(f"UPDATE {table} SET city = '{name}' WHERE id = {gid}")

        conn.commit()

    print("Calculated field city for subways")


def update_subway_colors(conn, osm_dir: Path):
    colors = {}

    with open(str(osm_dir / "color_keywords.csv"), "r") as f:
        for line in f:
            if len(line) < 3:
                continue
            color_key, color_hex, color_rgb = line.lower().strip().split('\t')
            colors[color_key.strip()] = color_hex.strip()

    print(f"Got {len(colors)} from colors file")

    cursor = conn.cursor(name='subway_lines_iterator')
    cursor_upd = conn.cursor()
    cursor.execute("SELECT DISTINCT ON(geometry) id, name, colour FROM osm_subway_route_members WHERE colour <> '' "
                   " and ST_GeometryType(geometry) = 'ST_LineString'")

    for row in cursor.fetchall():
        gid, name, colour = row
        colour = colour.strip().lower()
        res_colour = '#756a5e'

        if len(colour) > 0:
            if colour[0] == '#' and len(colour) == 7:
                cursor_upd.execute(f"UPDATE osm_subway_route_members SET handled=1 WHERE id={gid}")
                continue

            if colour in colors:
                res_colour = colors[colour]
            elif len(colour) == 6 or len(colour) == 3:
                try:
                    hex_num = int(colour, 16)
                    if len(colour) == 3:
                        res_colour = colour + colour
                    else:
                        res_colour = colour
                except Exception:
                    print(f"Could not convert {colour} to hex")

        print(f"Converted {colour} to {res_colour}")
        cursor_upd.execute(f"UPDATE osm_subway_route_members SET colour='{res_colour}', handled=1 WHERE id={gid}")

    conn.commit()


def preparation_subways(database_url: str, osm_dir: Path):
    print("Started preparing subways")
    conn = psycopg2.connect(database_url)
    tic = time.perf_counter()

    update_subways(conn)
    update_subway_colors(conn, osm_dir)

    conn.close()

    toc = time.perf_counter()
    print(f"Finished preparing subways in {toc - tic:0.1f} s")


if __name__ == "__main__":
    database_url = "postgresql://postgres:postgres_pass@homehub_maps_db/maps_db"
    preparation_subways(database_url)
