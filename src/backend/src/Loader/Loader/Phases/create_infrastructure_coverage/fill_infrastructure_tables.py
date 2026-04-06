import psycopg2
import time


IMPORTANCE_MAX = 10
IMPORTANCE_MIN = 1


def normalize(name):
    if name is None:
        return""

    s = name.lower().strip()
    skip_symbols = '"\'«»'
    for symbol in skip_symbols:
        s = s.replace(symbol, "")

    s = s.replace("ё", "е")
    return s


def get_poi_type(shop, amenity, healthcare):
    if shop in ["convenience", "supermarket", "mall", "greengrocer"]:
        return "shop"

    if healthcare in ["clinic"]:
        return "clinic"

    return amenity


def get_importance(parent_count):
    if parent_count == 0:
        return 0
    if parent_count < 10:
        return 1
    if parent_count < 50:
        return 2
    if parent_count < 100:
        return 3
    if parent_count < 200:
        return 4
    if parent_count < 500:
        return 5
    if parent_count < 1000:
        return 6
    if parent_count < 1500:
        return 7
    if parent_count < 2000:
        return 8
    if parent_count < 5000:
        return 9

    return 10


def get_poi_importance(brand_count, operator_count, item_count):
    return get_importance(brand_count) + get_importance(operator_count) + get_importance(item_count)


def remove_quotes(s):
    return s.replace('\'', "")


def fill_infrastrucutre_pois(conn):
    cursor = conn.cursor(name='infrastructure_cursor')
    cursorI = conn.cursor()
    cursor.itersize = 500

    objects = {}
    labels = {}

    cursor.execute(f"SELECT name, name_en, name_ru, operator, brand, shop, amenity, healthcare, ST_AsText(ST_Centroid(geometry))"
                   f" FROM osm_infrastructure_poly UNION ALL"
                   f" SELECT name, name_en, name_ru, operator, brand, shop, amenity, healthcare, ST_AsText(geometry)"
                   f" FROM osm_infrastructure_point")

    for row in cursor.fetchall():
        name, name_en, name_ru, operator, brand, shop, amenity, healthcare, geom_text = row
        if name is None or len(name) < 2:
            continue

        poi_type = get_poi_type(shop, amenity, healthcare)
        norm_name = normalize(name)
        norm_brand = normalize(brand)
        norm_operator = normalize(operator)


        if poi_type in ["shop", "pharmacy"]:
            if poi_type not in labels:
                labels[poi_type] = {}

            if len(norm_brand) > 1:
                if brand not in labels[poi_type]:
                    labels[poi_type][norm_brand] = 0
                labels[poi_type][norm_brand] += 1

            if len(norm_operator) > 1:
                if operator not in labels[poi_type]:
                    labels[poi_type][norm_operator] = 0
                labels[poi_type][norm_operator] += 1

        if poi_type not in objects:
            objects[poi_type] = {}

        if norm_name not in objects[poi_type]:
            objects[poi_type][norm_name] = {
                "name": name,
                "name_en": name_en,
                "name_ru": name_ru,
                "geom_list": [],
                "brand": norm_brand,
                "operator": norm_operator,
                "count": 0
            }

        objects[poi_type][norm_name]["count"] += 1
        objects[poi_type][norm_name]["geom_list"].append(geom_text)

    for poi_type, data_by_type in objects.items():
        for norm_name, data in data_by_type.items():
            if poi_type in ["shop", "pharmacy"]:
                poi_importance = get_poi_importance(labels[poi_type].get(data["brand"], 0), labels[poi_type].get(data["operator"], 0), data["count"])
            else:
                poi_importance = 10

            for geom in data["geom_list"]:
                cursorI.execute(f"INSERT INTO infrastructure_poi (poi_type, title, title_en, title_ru, importance, geometry)"
                                f" VALUES ('{poi_type}', '{remove_quotes(data['name'])}', "
                                f"'{remove_quotes(data['name_en'])}', '{remove_quotes(data['name_ru'])}',"
                                f"{poi_importance}, 'SRID=3857;{geom}')")

    conn.commit()


def calc_min_levels_for_pois(conn):
    min_level_to_hex_table = [
        [12, "hex_tiles_xl"],
        [11, "hex_tiles_xxl"],
        [9,  "hex_tiles_xxxl"],
        [8,  "hex_tiles_xxxxl"],
        [6,  "hex_tiles_xxxxxl"]
    ]

    for min_level, hex_table in min_level_to_hex_table:
        cursor = conn.cursor(name=f"cursor_{hex_table}")
        cursor.itersize = 1000

        cursor_infr = conn.cursor()

        cursor.execute(f"SELECT ST_AsText(ST_Centroid(geometry)), ST_AsText(geometry) from {hex_table}")

        for row in cursor.fetchall():
            hex_center, hex_geom = row
            cursor_infr.execute(f"SELECT gid, min_level FROM infrastructure_poi"
                                f" WHERE ST_Intersects(geometry,  'SRID=3857;{hex_geom}')"
                                f" ORDER BY ST_Distance(geometry, 'SRID=3857;{hex_center}') ASC"
                                f" LIMIT 10")

            first = True
            first_id = None
            set_id = False
            
            for row_infr in cursor_infr.fetchall():
                infr_id, infr_min_level = row_infr
                if first:
                    first_id = infr_id
                    first = True

                if infr_min_level is None:
                    cursor_infr.execute(f"UPDATE infrastructure_poi"
                                        f" SET min_level = {min_level}"
                                        f" WHERE gid = {infr_id}")
                    set_id = True
                    break
            
            if not set_id and first_id:
                cursor_infr.execute(f"UPDATE infrastructure_poi"
                    f" SET min_level = {min_level}"
                    f" WHERE gid = {first_id}")

            conn.commit()


def create_infrastructure_pois(database_url: str):
    print("Старт заполнения таблиц БД")
    conn = psycopg2.connect(database_url)
    print("Подключение к БД")
    tic = time.perf_counter()

    fill_infrastrucutre_pois(conn)
    print("Начало расчета минимальных значений уровня точек интереса инфраструктуры")
    calc_min_levels_for_pois(conn)
    print("Конец расчета минимальных значений уровня точек интереса инфраструктуры")

    if conn:
        conn.close()

    toc = time.perf_counter()
    print(f"Конец заполнения таблиц инфраструктуры {toc - tic:0.1f} s")


if __name__ == "__main__":
    create_infrastructure_pois()
