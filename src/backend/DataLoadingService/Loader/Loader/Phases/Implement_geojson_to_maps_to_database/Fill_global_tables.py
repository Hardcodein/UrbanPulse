import io
import json
import logging
import os
import shutil
import zipfile
import geopandas
import psycopg2
import requests
from shapely.geometry import Polygon

logger = logging.getLogger('import_geojson_to_maps_db')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

GEOJSON_DATA_LIST = [
    {
        "raw_file": "ne_10m_geography_marine_polys/ne_10m_ocean.shp",
        "borders_file": "oceans_clipped.geojson",
        "table": "world_oceans",
        "source_url": "https://naciscdn.org/naturalearth/10m/physical/ne_10m_ocean.zip",
        "need_to_create_subfolder": True
    },

    {
        "raw_file": "ne_10m_populated_places/ne_10m_populated_places.shp",
        "borders_file": "places_clipped.geojson",
        "table": "world_cities",
        "source_url": "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_populated_places.zip",
        "need_to_create_subfolder": True
    },
    {
        "raw_file": "ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp",
        "borders_file": "countries_clipped.geojson",
        "table": "world_countries",
        "source_url": "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip",
        "need_to_create_subfolder": True
    },
    {
        "raw_file": "water-polygons-split-4326/water_polygons.shp",
        "borders_file": "oceans_detailed_clipped.geojson",
        "table": "world_oceans_detailed",
        "source_url": "https://osmdata.openstreetmap.de/download/water-polygons-split-4326.zip",
        "need_to_create_subfolder": False
    }
]
SCALE = 0
EMPTY_VALUE = ""

CRS_WGS84 = {"type": "name", "properties": {"name": "EPSG:4326"}}

# Получение файла по пути
def get_filename_from_url(url):
    assert url.find("/")
    return url.rsplit("/", 1)[1]


def download_file(url, data_path_string: str):

    file_name = get_filename_from_url(url)

    logger.info(f"Начало загрузки {url}")

    try:
        response = requests.get(url, 
                                allow_redirects=True, 
                                stream=True, 
                                headers={"User-Agent": "UrbanPulse"})
    except Exception as e:
        logger.exception(f" Не удалось загрузить {url}")
        raise

    if response.status_code != 200:
        error_message = f"Ошибка {response.status_code} при загрузке {url}"
        logger.error(error_message)
        raise Exception(error_message)

    all_path_file = os.path.join(data_path_string, file_name)

    with open(all_path_file, 'wb') as file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, file)

    return all_path_file


def extract_archive(src_archive, dst_path):
    with zipfile.ZipFile(src_archive, "r") as zip_ref:
        zip_ref.extractall(dst_path)


def prepare_files(data, data_path: str):
    filepath = data["raw_file"]

    if os.path.isfile(os.path.join(data_path, filepath)):
        logger.info(f"{filepath} существует")
        return

    path, filename  = filepath.split("/")
    
    zip_path = download_file(data["source_url"], data_path)

    logger.info(f"Скачан файл {zip_path}")

    if data["need_to_create_subfolder"]:
        extract_archive(zip_path, os.path.join(data_path, path))
    else:
        extract_archive(zip_path, data_path)

    logger.info(f"Распакован {zip_path}")


def init_main_tables(database_url: str, data_path: str):
    
    connection = psycopg2.connect(database_url)

    cursor = connection.cursor()

    for data_item in GEOJSON_DATA_LIST:

        logger.info(f"Выборка {data_item['table']}")

        path = os.path.join(data_path, data_item["borders_file"])

        if not (os.path.isfile(path)):


            prepare_files(data_item, data_path)

            print(f" Путь посл prepare {data_path}")
            print(f"GeoPandas: {geopandas.__version__}")
            shape_file = geopandas.read_file(os.path.join(data_path, data_item["raw_file"]))
            print(f"Парсинг окончен")
            logger.info("Парсинг окончен")

            if data_item["table"] == "world_oceans_detailed":
                polygon = Polygon(
                [(-180.0, 0), 
                 (-180.0, 89.0), 
                 (180.0, 89.0), 
                 (180.0, 0)]
                )
            else:
                polygon = Polygon(
                [
                    (-180.0, -89.0),
                    (-180.0, 89.0),
                    (180.0, 89.0),
                    (180.0, -89.0),
                ]
            )

            world_clipped = geopandas.clip(shape_file, polygon)

            logger.info("Обрезка")

            filepath = os.path.join(data_path, data_item["borders_file"])

            world_clipped.to_file(filepath, driver="GeoJSON")

            logger.info("Файл сохранен")
        else:
            filepath = os.path.join(data_path, data_item["borders_file"])
            print(data_item["borders_file"]+" существует")

        with io.open(filepath,encoding='utf-8') as file:
            logger.info("Файл открыт")
            data = json.load(file)

            for object in data["features"]:

                if "geometry" not in object or object["geometry"] is None:
                    logger.warning("Нет геометии. Skip.")
                    continue

                properties = dict(
                    (k.lower(), v) for k, v in object["properties"].items()
                )

                scalerank = int(properties.get("min_label", SCALE))

                stype = properties.get("featurecla", EMPTY_VALUE)

                name = EMPTY_VALUE

                if "name" in properties and properties["name"] is not None:
                    name = properties["name"]
                    name = name.replace("'", " ")

                name_ru = EMPTY_VALUE
                if "name_ru" in properties and properties["name_ru"] is not None:
                    name_ru = properties["name_ru"]
                    name_ru = name_ru.replace("'", " ")
                    if name_ru == "Алма-Ата":
                        name_ru = "Алматы"

                name_en = EMPTY_VALUE
                if "name_en" in properties and properties["name_en"] is not None:
                    name_en = properties["name_en"]
                    name_en = name_en.replace("'", " ")
                
                

                object["geometry"]["crs"] = CRS_WGS84

                geo_json = json.dumps(object["geometry"])

                table = data_item["table"]

                cursor.execute(
                    f"INSERT INTO {table} (scalerank, type, name, name_ru, name_en, geometry) "
                    f"VALUES ({scalerank}, '{stype}', '{name}', '{name_ru}', '{name_en}', "
                    f"ST_TRANSFORM(ST_MakeValid(ST_GeomFromGeoJSON('{geo_json}')), 3857))"
                )
            logger.info("Окончена загрузка в "+ data_item["table"])

        logger.info("Окончена загрузка в БД")

    connection.commit()



