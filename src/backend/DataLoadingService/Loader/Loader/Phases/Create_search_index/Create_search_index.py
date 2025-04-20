# -*- coding: utf-8 -*-

import argparse
import psycopg2
import time
import os
import math
import logging


TOWNS_RATING = {
    "city": 10,
    "town": 6,
    "village": 3,
    "hamlet": 2,
    "isolated_dwelling": 1
}

ROADS_RATING = {
    "motorway": 10,
    "motorway_link": 10,
    "trunk": 10,
    "trunk_link": 10,
    "primary": 9,
    "primary_link": 9,
    "secondary": 8,
    "secondary_link": 8,
    "tertiary": 7,
    "tertiary_link": 7,
    "road": 5,
    "street": 5,
    "residential": 5,
    "living_street": 5,
    "street_limited": 4,
    "track": 2,
    "raceway": 1,
    "service": 1,
    "unclassified": 1
}

PLACE_RATING = 5
QUARTER_RATING = 5
POPULATION_MAX = 12630289


def get_city_rating(city_type):
    return TOWNS_RATING.get(city_type, 3)


def get_road_rating(road_type):
    return ROADS_RATING.get(road_type, 5)


def get_population_rating(population):
    return int(population / POPULATION_MAX * 10)


def get_count(cursor, table):
    cursor.execute(f"SELECT count(*) FROM {table} WHERE name <> ''")
    count = cursor.fetchone()[0]
    return count


def get_dist(c1, c2):
    lon1, lat1 = c1
    lon2, lat2 = c2
    earth_r = 6378137.0

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = math.sin(dLat / 2.0) * math.sin(dLat / 2.0) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2.0) * math.sin(dLon / 2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return earth_r * c


def build_towns(conn, res_file):
    cursor_count = conn.cursor()
    table = "osm_place_point"
    count = get_count(cursor_count, table)

    res_file.write(f"{count}\n")

    logging.info(f"{count} towns with names. {count} from {table}")
    cities = {}

    cursor = conn.cursor(name=f'iterator_towns_{table}')
    cursor.itersize = 1000
    cursor.execute(f"SELECT DISTINCT ON (id) id, name,"
                   f" ST_X(ST_Transform(geometry, 4326)),"
                   f" ST_Y(ST_Transform(geometry, 4326)),"
                   f" type, population"
                   f" FROM {table}  WHERE name <> ''")

    for row in cursor.fetchall():
        town_id, name, lon, lat, town_type, population = row

        is_same_city = False

        city_data = {
            "coords": (lon, lat),
            "town_id": town_id,
            "type": town_type,
            "population": population
        }

        if name in cities:
            for item in cities[name]:
                dist = get_dist([lon, lat], item["coords"])
                if dist < 15000:
                    is_same_city = True
                    if (item["population"] is None or item["population"] == 0) \
                            and population is not None and population > 0:
                        item["population"] = population
                    break
            if is_same_city:
                continue
            cities[name].append(city_data)
        else:
            cities[name] = [city_data]

    res_count = 0

    town_ids = set()
    for name, data in cities.items():
        multiple = False
        if len(data) > 1:
            logging.info(f"{name} For this name there are {len(data)} populated places.")
            multiple = True

        for item in data:
            if item["population"] is not None and item["population"] > 0:
                town_rating = get_population_rating(item["population"])
            else:
                town_rating = get_city_rating(item["type"])

            town_id = item["town_id"]
            assert town_id not in town_ids
            town_ids.add(town_id)

            lon, lat = item['coords']

            if multiple:
                logging.info(f"\t{name}\t{item['type']}\t{lat} {lon}")

            arr_data = [town_id, f'{lon:.4f}', f'{lat:.4f}', town_rating, name]
            record = "\n".join(str(x) for x in arr_data)
            res_file.write(f"{record}\n")
            res_count += 1

    logging.info(f"Finished building towns. Saved {res_count} places.")
    return town_ids


def get_nearest_town(cursor, town_ids, geom, max_dist):
    # Search for nearest town:
    min_dist = -1
    town_id = ""

    table = "osm_place_poly"
    cursor.execute(f"SELECT id, ST_Distance(geometry, 'SRID=3857;{geom}')"
                   f" FROM {table} "
                   f" ORDER BY ST_Distance(geometry, 'SRID=3857;{geom}') ASC "
                   f" LIMIT 10")

    for t_row in cursor.fetchall():
        tid, dist = t_row
        if tid not in town_ids:
            continue
        if dist is None:
            continue
        if min_dist == -1 or dist < min_dist:
            min_dist = dist
            town_id = tid

    if min_dist > max_dist or min_dist == -1:
        return None

    return town_id


def get_name(layer_id, obj_name):
    if layer_id == "subway_stations":
        return "Метро " + obj_name
    return obj_name


def build_multipart_objects(conn, res_file, town_ids, table, layer_id):
    cursor_helper = conn.cursor()
    cursor = conn.cursor(name=f'iterator_{table}')
    cursor.itersize = 500

    d = {}
    obj_count = 0

    obj_type = "''"
    if layer_id != "subway_stations":
        obj_type = f"{table}.type"

    cursor.execute(f"SELECT DISTINCT ON ({table}.id)"
                   f" {table}.id, {obj_type}, {table}.name, {table}.geometry,"
                   f" osm_place_poly.id"
                   f" FROM {table}"
                   f" LEFT JOIN osm_place_poly"
                   f" ON ST_Intersects({table}.geometry, osm_place_poly.geometry)"
                   f" WHERE {table}.name <> ''")

    for i, row in enumerate(cursor.fetchall()):
        obj_id, obj_type, obj_name, obj_geom, city_id = row

        if layer_id == "street":
            rating = get_road_rating(obj_type)
        else:
            rating = 5.0

        # Search for nearest town:
        if city_id is None or city_id not in town_ids:
            city_id = get_nearest_town(cursor_helper, town_ids, obj_geom, 2000)

        if city_id is None:
            city_id = 0

        if city_id not in d:
            d[city_id] = {}

        if obj_name not in d[city_id]:
            d[city_id][obj_name] = {
                "geoms": [obj_geom],
                "rating": rating
            }
            obj_count += 1
        else:
            d[city_id][obj_name]["geoms"].append(obj_geom)
            if rating > d[city_id][obj_name]["rating"]:
                d[city_id][obj_name]["rating"] = rating

        if i % 10000 == 0:
            logging.info(f"Handled {i} objects in {layer_id}")

    res_file.write(f"{obj_count}\n")

    for city_id, city_objects in d.items():
        for obj_name, obj_data in city_objects.items():
            geometries = ",".join(f"'SRID=3857;{g}'" for g in obj_data["geoms"])
            query = f"SELECT ST_AsGeoJSON(ST_Transform(ST_Collect(ARRAY[{geometries}]), 4326))"

            cursor_helper.execute(query)
            union_geom = cursor_helper.fetchone()[0]

            arr_data = [str(union_geom), layer_id, city_id, obj_data["rating"], get_name(layer_id, obj_name)]
            record = "\n".join(str(x) for x in arr_data)
            res_file.write(f"{record}\n")

    logging.info(f"Finished building {layer_id}")


def build_addresses(conn, res_file, town_ids):
    layer_id = "buildings"

    cursor_helper = conn.cursor()
    cursor = conn.cursor(name=f'iterator_addresses')
    cursor.itersize = 300

    buildings_filter = "housenumber <> '' and (street <> '' or quarter <> '')"
    cursor_helper.execute(f"SELECT count(*) FROM osm_buildings_poly WHERE {buildings_filter}")

    count = cursor_helper.fetchone()[0]
    res_file.write(f"{count}\n")

    logging.info(f"{count} addresses with housenumbers and streets or quarters")

    cursor.execute(f"SELECT DISTINCT ON (osm_buildings_poly.id)"
                   f" osm_buildings_poly.id, ST_AsText(osm_buildings_poly.geometry),"
                   f" ST_AsGeoJSON(ST_Transform(osm_buildings_poly.geometry, 4326)),"
                   f" street, quarter, housenumber,"
                   f" osm_roads_way.type as road_type"
                   f" FROM osm_buildings_poly "
                   f" LEFT JOIN osm_roads_way on osm_roads_way.name = street "
                   f" and ST_Distance(osm_roads_way.geometry, osm_buildings_poly.geometry) < 1000.0"
                   f" WHERE {buildings_filter}")

    for i, row in enumerate(cursor.fetchall()):
        bld_id, bld_geom, bld_geom_json, street, quarter, housenumber, street_type = row

        if quarter == '':
            street_rating = get_road_rating(street_type)

            if street_type is None:
                logging.info(f"Could not find nearest street for {bld_id}. Type: {street_type}. "
                      f"Street: {street}. Housenumber: {housenumber}")
        else:
            street_rating = 5
            street = quarter

        # Search for nearest town:
        town_id = get_nearest_town(cursor_helper, town_ids, bld_geom, 3000)

        if town_id is None:
            town_id = 0

        arr_data = [bld_geom_json, "building", town_id, street_rating, f"{street}, {housenumber}"]
        record = "\n".join(str(x) for x in arr_data)

        res_file.write(f"{record}\n")

        if i % 10000 == 0:
            logging.info(f"Handled {i}/{count} addresses with streets or quarters.")

    logging.info("Finished building addresses with streets or quarters.")


def main_create_index(database_url_string: str, dst_directory):

    logging.info("Начало создания индексов")

    conn = psycopg2.connect(database_url_string)
    logging.info("Подключено к БД")

    tic = time.perf_counter()

    # TOWNS
    with open(os.path.join(dst_directory, "towns.txt"), 'w') as resources_file:
        town_ids = build_towns(conn, resources_file)

    # RESIDENTIAL AREAS
    with open(os.path.join(dst_directory, "residential.txt"), 'w') as resources_file:
        build_multipart_objects(conn, resources_file, town_ids, "osm_residential_zones", "residential")

    # STREETS
    with open(os.path.join(dst_directory, "roads.txt"), 'w') as resources_file:
        build_multipart_objects(conn, resources_file, town_ids, "osm_roads_way", "roads")

    # SUBWAYS
    with open(os.path.join(dst_directory, "subway_stations.txt"), 'w') as resources_file:
        build_multipart_objects(conn, resources_file, town_ids, "osm_subway_stations", "subway_stations")

    # ADDRESSES
    with open(os.path.join(dst_directory, "buildings.txt"), 'w') as resources_file:
        build_addresses(conn, resources_file, town_ids)

    if conn:
        conn.close()

    toc = time.perf_counter()
    logging.info(f"Finished building index in {toc - tic:0.1f} s")


def wait_for_file(filename):
    
    if len(filename) > 0:
        logging.info(f"Waiting for {filename} creation to start seeding.")
        tic = time.perf_counter()

        while not os.path.exists(filename):
            time.sleep(60)

        toc = time.perf_counter()
        logging.info(f"Finished waiting for {filename} in {toc - tic:0.4f} s")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-dst", "--dst", type=str, help="Dst dir.")
    args = parser.parse_args()
    database_url = ...
    wait_for_file("/data/finished_tiles_generation.txt")
    main_create_index(database_url, args.dst)
