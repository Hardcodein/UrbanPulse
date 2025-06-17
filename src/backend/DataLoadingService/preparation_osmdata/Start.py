# -*- coding: utf-8 -*-

import argparse
import os
import json

geofabrik_url = "http://download.geofabrik.de"


def run_commandLine(cmd_string):
    ret_res = os.system(cmd_string)
    if ret_res != 0:
        print(f"Error {ret_res} running {cmd_string}")
        exit()


def get_cities_list(string):
    cities = string.lower().strip().split(',')
    if len(cities) == 1 and cities[0] == "all":
        return []


def main():
    argumentParser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argumentParser.add_argument('-d', 
                                '--dir', 
                                required=True,
                                help='Output directory for downloaded files.')

    argumentParser.add_argument('-c', 
                                '--cities', 
                                required=False, 
                                default="",
                                help="List of cities separated by commas.")

    args = argumentParser.parse_args()

    cities_list = get_cities_list(args.cities)

    with open(os.path.join(args.dir, 'implement_cities.json')) as json_file:
        supported_cities = json.load(json_file)

    files_for_del = set()

    for city_item in supported_cities["cities"]:
        name_en = city_item["title_en"]

        if len(cities_list) > 0 and name_en not in cities_list:
            print("Пропуск", name_en)
            continue

        print("Выборка", name_en)
        osm_file_full = city_item["osm_extract_file"]
        geojson_clip_area = name_en + "_borders_for_osmium_extract.geojson"
        osm_file_clipped = name_en + ".osm.pbf"

        path_file = os.path.join(args.dir, osm_file_full)
        path_geojson = os.path.join(args.dir, geojson_clip_area)
        path_file_clipped = os.path.join(args.dir, osm_file_clipped)

        if not os.path.exists(path_file):
            print(f"Downloading {city_item['osm_extract_file']} from geofabrik")
            run_commandLine(f"wget {geofabrik_url}/{city_item['geofabrik_path']}/{city_item['osm_extract_file']} -P {args.dir}")


        print(f"Extracting {osm_file_clipped}")
        run_commandLine(f"osmium extract -p {path_geojson} {path_file} -o {path_file_clipped}")
        files_for_del.add(path_file)

    print("Finished extracting cities. Deleting huge osm.pbf files.")
    for file in files_for_del:
        os.remove(file)
        print(f"{file} is deleted")
    
    print("Finished preparing osm data.")


if __name__ == '__main__':
    main()
