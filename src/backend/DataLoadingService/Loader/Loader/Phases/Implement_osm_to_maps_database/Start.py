import json
import os

from typing import List


def start_commandLine(string_cmd):

    ret_res = os.system(string_cmd)

    if ret_res != 0:
        errorMessage = f"Ошибка {ret_res} выполения {string_cmd}"
        raise Exception(errorMessage)


def get_cities_list(s):
    cities = s.lower().strip().split(',')
    if len(cities) == 1 and cities[0] == "all":
        return []


def main(database_url_string: str, 
         resources_directory: str, 
         osm_directory: str, 
         cities_list: List[str]):
    dir = os.listdir()
    with open(os.path.join(osm_directory, 'implement_cities.json'), "r", encoding="utf-8") as json_file:
        implement_cities_list = json.load(json_file)

    for city_item in implement_cities_list["cities"]:

        name_city = city_item["title_en"]

        if len(cities_list) > 0 and name_city not in cities_list:
            print("Пропуск", name_city)
            continue

        print("Выборка из ", name_city)

        path_file = os.path.join(osm_directory, name_city + ".osm.pbf")

        mapping_path = os.path.join(resources_directory, 'mapping.yaml')

        cmd = f"/go/imposm-0.14.1-linux-x86-64/imposm import " \
              f" -connection {database_url_string}" \
              f" -read {path_file}" \
              f" -mapping {mapping_path}" \
              f" -write -deployproduction" \
              f" -appendcache"

        start_commandLine(cmd)

        print("Loaded", name_city, "to PostgreSQL")


def start_phase(database_url: str,
                resources_directory: str,
                osm_directory: str, 
                cities_list: List[str]) -> None:
    
    main(database_url, resources_directory, osm_directory, cities_list)
