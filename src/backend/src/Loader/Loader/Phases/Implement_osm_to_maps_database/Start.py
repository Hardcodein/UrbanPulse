import json
import os
import urllib.request

from typing import List


def start_commandLine(string_cmd):

    ret_res = os.system(string_cmd)

    if ret_res != 0:
        errorMessage = f"Ошибка {ret_res} выполения {string_cmd}"
        raise Exception(errorMessage)


def download_pbf(url: str, dest_path: str) -> None:
    """Скачивает PBF файл с прогрессом если его ещё нет."""
    print(f"Скачивание {url}")
    print(f"  -> {dest_path}")

    def reporthook(count, block_size, total_size):
        if total_size > 0:
            percent = count * block_size * 100 // total_size
            mb_done = count * block_size // (1024 * 1024)
            mb_total = total_size // (1024 * 1024)
            print(f"\r  {percent}% ({mb_done}/{mb_total} МБ)", end='', flush=True)

    urllib.request.urlretrieve(url, dest_path, reporthook)
    print()  # перевод строки после прогресса
    print("Скачивание завершено.")


def main(database_url_string: str,
         resources_directory: str,
         osm_directory: str,
         cities_list: List[str]):
    with open(os.path.join(osm_directory, 'implement_cities.json'), "r", encoding="utf-8") as json_file:
        implement_cities_list = json.load(json_file)

    for city_item in implement_cities_list["cities"]:

        name_city = city_item["title_en"]

        if len(cities_list) > 0 and name_city not in cities_list:
            print("Пропуск", name_city)
            continue

        print("Выборка из ", name_city)

        pbf_filename = city_item["osm_extract_file"]
        path_file = os.path.join(osm_directory, pbf_filename)

        # Автоматически скачиваем PBF если файла ещё нет
        if not os.path.exists(path_file):
            geofabrik_url = city_item.get("geofabrik_url")
            if not geofabrik_url:
                raise FileNotFoundError(
                    f"Файл {path_file} не найден и geofabrik_url не указан в implement_cities.json"
                )
            download_pbf(geofabrik_url, path_file)
        else:
            print(f"Файл {pbf_filename} уже есть, скачивание пропущено.")

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
