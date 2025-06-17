import argparse
import concurrent.futures
import math
import os
import time
import json

from pathlib import Path

import psycopg2
from configuraton import *
#from Loader.Phases.Create_tiles.configuraton import *

cities_borders = {}


def get_geometry(geometry_operator):

    if geometry_operator is None:
        return "geometry", "geometry"

    if geometry_operator == "line_merge":
        return "ST_LineMerge(ST_Collect(geometry))", "geometry"

    if geometry_operator == "centroid":
        return "ST_Centroid(geometry)", "ST_Centroid(geometry)"

    assert False


def get_query(table, 
              new_layer_name, 
              fields, 
              x, y, z, 
              additional_where, 
              geometry_operator, 
              city):
    
    geom_select, geom_where = get_geometry(geometry_operator)

    fields_string = ""

    if len(fields) > 0:
        fields_string = f"{fields},"

    return f" (SELECT ST_AsMVT(q_{new_layer_name}, '{new_layer_name}', 4096, 'geom')\
        FROM (\
          SELECT {fields_string} ST_AsMvtGeom({geom_select}, BBox({x}, {y}, {z}), 4096, 64, true) AS geom\
          FROM {table}\
          WHERE ST_Intersects({geom_where}, BBox({x}, {y}, {z})) {additional_where} \
        ) as q_{new_layer_name}) "

# Преобразование из геогфических коордиинат в WebMercator
def geographical_coordinats_to_tiles(lat_lon_arr, zoom):
    lat_deg = lat_lon_arr[0] # широта
    lon_deg = lat_lon_arr[1] # долгота

    lat_rad = math.radians(lat_deg)

    if zoom == 0:
        n = 1
    else:
        n = 2.0 ** zoom

    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    return [xtile, ytile]


def generate_tile(connection, 
                  cur_x_path, 
                  x, 
                  y, 
                  z, 
                  source_data, 
                  city=None):
    
    cursor = connection.cursor()

    cur_y_filename = f"{y}.pbf"
    cur_y_tile = cur_x_path + cur_y_filename

    query_all_layers = "SELECT "

    layer_names_set = set()

    first = True

    for layer_item in layers:

        if "source" in layer_item and layer_item["source"] != source_data["name"]:
            continue

        if "source" not in layer_item and source_data["name"] != default_source:
            continue

        layer_name = layer_item["layer_name"]

        max_z = source_data["def_max_zoom"] if "max_zoom" not in layer_item else layer_item["max_zoom"]
        min_z = source_data["def_min_zoom"] if "min_zoom" not in layer_item else layer_item["min_zoom"]

        if z < min_z or z > max_z:
            continue

        assert (layer_name not in layer_names_set)
        layer_names_set.add(layer_name)

        assert ("fields" in layer_item)
        query_fields = layer_item["fields"]
        query_filter = ""

        if "additional_where" in layer_item:
            query_filter = layer_item["additional_where"]
            if "append_zoom_to_additional_where" in layer_item:
                query_filter += str(z)

        query = get_query(layer_item["table"], layer_name, query_fields, x, y, z, query_filter,
                      layer_item.get("geometry_operator", None), city)

        if first:
            query_all_layers += query
            first = False
        else:
            query_all_layers += " || " + query

    try:
        cursor.execute(query_all_layers)
    except psycopg2.errors.SyntaxError as e:
        print(query_all_layers)
        print(e)
        raise

    bin_data = cursor.fetchone()[0]

    
    with open(cur_y_tile, 'wb') as f:
        f.write(bin_data)
    

    return True


def seed_tiles_for_source(source_data, 
                          threads_count, 
                          tiles_path, 
                          conn, 
                          point1,
                          point2, 
                          city=None):
    source_name = source_data["name"]

    for zoom_item in source_data["zoom_levels"]:

        x1, y1 = geographical_coordinats_to_tiles(point1, zoom_item)
        x2, y2 = geographical_coordinats_to_tiles(point2, zoom_item)

        x_start, x_finish = min(x1, x2), max(x1, x2)
        y_start, y_finish = min(y1, y2), max(y1, y2)

        x_tile_count = abs(x_finish - x_start) + 1
        y_tile_count = abs(y_finish - y_start) + 1

        print(
            f'{source_name}. Started handling zoom = {zoom_item}, bbox: (x_start={x_start}, '
            f'y_start={y_start}) - (x_finish={x_finish}, y_finish={y_finish}). '
            f'x tiles count = {x_tile_count}, y tiles count = {y_tile_count}, '
            f'total count = {x_tile_count * y_tile_count}')

        tic = time.perf_counter()

        for x in range(x_start, x_finish + 1):

            if(x == 76):
                continue

            cur_x_path = os.path.join(tiles_path, f"{zoom_item}/{x}/")

            if not os.path.exists(cur_x_path):
                os.makedirs(cur_x_path)

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads_count) as executor:

                future_tiles = {executor.submit(generate_tile, conn, cur_x_path, x, y, zoom_item, source_data, city):
                                    y for y in range(y_start, y_finish + 1, 1)}

                for future in concurrent.futures.as_completed(future_tiles):
                    done = future.result()
                    if not done:
                        print(f"Error handling tile {future}")

        toc = time.perf_counter()
        print(f"Finished handling zoom {zoom_item} for {source_name} in {toc - tic:0.4f} s")


def cut_borders_city(connection, 
                     implement_cities, 
                     osm_directory_path: Path):
    
    global cities_borders

    cursor = connection.cursor()

    for city_item in implement_cities["cities"]:

        city_title_en = city_item["title_en"]

        with open(str(osm_directory_path / f'{city_title_en}_borders_for_clipping.geojson'), "r", encoding="utf-8") as borders_file:

            borders_str = borders_file.readline().strip()

            cursor.execute(f"SELECT ST_AsText(ST_Transform(ST_GeomFromGeoJSON('{borders_str}'),3857))")

            borders3857_str = cursor.fetchone()[0]

            cities_borders[city_title_en] = f"SRID=3857;{borders3857_str}"

        print(f"Заполнены границы для {city_title_en}")


def main_create_tiles(database_url_string: str, 
                      osm_directory: Path, 
                      root_tiles_path: Path, 
                      threads_count, 
                      source=None, 
                      town=None):

    with open(str(osm_directory / 'implement_cities.json'), "r", encoding="utf-8") as json_file:
        supported_cities = json.load(json_file)

    print(f"Обработано {len(supported_cities['cities'])} городов.")

    connection = psycopg2.connect(database_url_string)
    print(f"Подключение к БД. Количество потоков: {threads_count}.")

    tic_start = time.perf_counter()

    cut_borders_city(connection, supported_cities, osm_directory)

    for source_data in sources:

        source_name = source_data["name"]

        if source and source_name != source:
            print("Пропуск источника", source_name)
            continue

        tiles_path = str(root_tiles_path / source_name)

        if not os.path.exists(tiles_path):
            os.makedirs(tiles_path)

        # 2 points for building bbox:
        point1 = source_data.get("bbox_p1_deg", [])
        point2 = source_data.get("bbox_p2_deg", [])

        if len(point1) == 0:
            # Seed this source tiles for all supported cities.
            for city in supported_cities["cities"]:
                if town and city["title_en"] != town:
                    print("Пропуск города", city["title_en"])

                borders = city["borders_for_tiles"]

                point1 = [borders["west_south"]["lat"], borders["west_south"]["lon"]]
                point2 = [borders["east_north"]["lat"], borders["east_north"]["lon"]]

                print(f"Started seeding {source_name} for {city['title_en']}")

                seed_tiles_for_source(source_data, threads_count, tiles_path, connection, point1, point2, city['title_en'])
        else:
            # Начальные плитки для ограничивающего прямоугольника из конфигурации bounding box.
            seed_tiles_for_source(source_data, threads_count, tiles_path, connection, point1, point2)

    if connection:
        connection.close()

    toc_end = time.perf_counter()
    print(f"Закончена обрезка городов {toc_end - tic_start:0.4f} s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--threads", type=int, default=THREADS_COUNT,
                        help="threads count for seeding tiles.")

    parser.add_argument("-s", "--source", type=str,
                        help="source which should be seeded.")

    parser.add_argument("-b", "--begin", type=str, default="", help="start seeding when the specified file is created.")

    args = parser.parse_args()

    main_create_tiles(args.threads, args.source)
