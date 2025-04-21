from pathlib import Path

import psycopg2
import json
import time
import os

import Loader.Phases.Preparation_tables.UseConst as u

#Добавление в таблицу колонок  плотность и процент застройки
def add_density_columns_for_buildings(contection):
    con_cursor = contection.cursor()

    for table_item in ["osm_buildings_poly", "osm_building_parts_poly"]:
        con_cursor.execute(f"ALTER TABLE {table_item} "
                        f"ADD COLUMN  IF NOT EXISTS pct_building numeric,"
                        f"ADD COLUMN  IF NOT EXISTS pct_dens_building numeric,"
                        f"ADD COLUMN  IF NOT EXISTS pct_human_density numeric")
    contection.commit()

# Границы городов
def fill_borders_cities(connection, 
                        osm_directory_path: Path):

    cities_borders = {}

    with open(str(osm_directory_path / 'implement_cities.json'), "r", encoding="utf-8") as json_file:
        implement_cities_list = json.load(json_file)
        
    print(f"Внедрено {len(implement_cities_list['cities'])} городов.")

    con_cursor = connection.cursor()
    
    for city_item in implement_cities_list["cities"]:

        city_title = city_item["title_en"]

        with open(str(osm_directory_path / f'{city_title}_borders_for_clipping.geojson'), "r", encoding="utf-8") as borders_file:

            borders_string = borders_file.readline().strip()
             #Читает файлы с границами городов (*_borders_for_clipping.geojson).
            con_cursor.execute(f"SELECT ST_AsText(geometry), {u.QUERY_COEF} FROM"
                           f"(SELECT ST_Transform(ST_GeomFromGeoJSON('{borders_string}'),3857) as geometry) as q")
            
            borders3857_str, coef = con_cursor.fetchone()
            #Конвертирует их в формат PostGIS (SRID=3857 — Web Mercator).
            cities_borders[city_title] = [f"SRID=3857;{borders3857_str}", coef]

        print(f"Внесены границы для {city_title}")

    return cities_borders



def create_hex_tables(conn):
    tables = {"hex_tiles": u.HEX_R,
              "hex_tiles_s": u.HEX_R * 3,
              "hex_tiles_m": u.HEX_R * 6,
              "hex_tiles_l": u.HEX_R * 9,
              "hex_tiles_xl": u.HEX_R * 12,
              "hex_tiles_xxl": u.HEX_R * 40,
              "hex_tiles_xxxl": u.HEX_R * 80,
              "hex_tiles_xxxxl": u.HEX_R * 120,
              "hex_tiles_xxxxxl": u.HEX_R * 240,
              }

    for table, _ in tables.items():
        commands = [f"DROP TABLE IF EXISTS {table}",
                    f"CREATE TABLE {table} "
                    f"(gid serial, impact int default 0, bld_dens_pct int, bld_human_density int, bld_pct int, infrastructure int, "
                    f"filter_subway smallint, filter_park smallint, filter_kindergarten smallint, "
                    f"filter_school smallint, filter_shop smallint, filter_where_to_eat smallint, "
                    f"life_quality smallint)",
                    f"ALTER TABLE {table} ADD PRIMARY KEY (gid)",
                    f"SELECT AddGeometryColumn('', '{table}', 'geometry', 3857, 'GEOMETRY', 2)"
                    ]

        commands.append(f"CREATE INDEX {table}_geom_idx ON {table} USING GIST(geometry)")

        cursor = conn.cursor()

        for command in commands:
            cursor.execute(command)
            conn.commit()


def add_infrastructure_columns(conn):
    cursor = conn.cursor()

    for table in ["osm_buildings_poly", "osm_building_parts_poly"]:
        cursor.execute(f"ALTER TABLE {table} "
                        f"ADD COLUMN  IF NOT EXISTS infrastructure numeric")
    conn.commit()


def create_infrastructure_tables(conn):
    cursor = conn.cursor()

    table = "infrastructure_poi"
    commands = [f"DROP TABLE IF EXISTS {table}",
            f"CREATE TABLE {table} (gid serial, poi_type text, title text, "
            f"title_en text, title_ru text, importance int, min_level int)",
            f"ALTER TABLE {table} ADD PRIMARY KEY (gid)",
            f"SELECT AddGeometryColumn('', '{table}', 'geometry', 3857, 'GEOMETRY', 2)",
            f"CREATE INDEX {table}_geom_idx ON {table} USING GIST(geometry)",
            ]

    for command in commands:
        cursor.execute(command)
        conn.commit()


def add_is_drawable_building_columns(conn):
    cursor = conn.cursor()

    for table in ["osm_buildings_poly", "osm_building_parts_poly"]:
        cursor.execute(f"ALTER TABLE {table} "
                       f"ADD COLUMN  IF NOT EXISTS is_drawable smallint")
    cursor.execute(f"ALTER TABLE osm_building_parts_poly "
                   f"ADD COLUMN  IF NOT EXISTS type text")
    conn.commit()


def add_subway_columns(conn):
    cursor = conn.cursor()
    tables = ["osm_subway_stations", "osm_subway_station_entrances"]
    for table in tables:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS city varchar")

    cursor.execute(f"ALTER TABLE osm_subway_route_members ADD COLUMN IF NOT EXISTS handled int default 0")
    conn.commit()


def create_global_tables(conn):
    cursor = conn.cursor()
    for table in ["world_oceans", "world_oceans_detailed", "world_countries", "world_cities"]:
        commands = [
            f"DROP TABLE IF EXISTS {table}",
            f"CREATE TABLE {table} (gid serial, scalerank int4, type varchar(80),"
            f" name varchar(80), name_ru varchar(80), name_en varchar(80))",
            f"ALTER TABLE {table} ADD PRIMARY KEY (gid)",
            f"SELECT AddGeometryColumn('', '{table}', 'geometry', 3857, 'GEOMETRY', 2)",
            f"CREATE INDEX {table}_geom_idx ON {table} USING GIST(geometry)",
        ]

        for command in commands:
            cursor.execute(command)
            conn.commit()


def wait_for_file(filename):
    if len(filename) > 0:
        print(f"Waiting for {filename} creation to start seeding.")
        tic = time.perf_counter()

        while not os.path.exists(filename):
            time.sleep(60)

        toc = time.perf_counter()
        print(f"Finished waiting for {filename} in {toc - tic:0.4f} s")


def create_tables(database_url: str):
    conn = psycopg2.connect(database_url)
    print("Connected to db")
    tic = time.perf_counter()

    create_global_tables(conn)
    add_density_columns_for_buildings(conn)
    create_hex_tables(conn)
    add_infrastructure_columns(conn)
    create_infrastructure_tables(conn)
    add_is_drawable_building_columns(conn)
    add_subway_columns(conn)


    if conn:
        conn.close()

    toc = time.perf_counter()

    print(f"Finished creating tables in {toc - tic:0.1f} s")


if __name__ == "__main__":
    wait_for_file("/data/finished_osm_import.txt")
    database_url = "postgresql://postgres:postgres_pass@homehub_maps_db/maps_db"
    create_tables(database_url)

    with open('/data/finished_tables_preparation.txt', 'w') as f:
        f.write(f"Done work.")