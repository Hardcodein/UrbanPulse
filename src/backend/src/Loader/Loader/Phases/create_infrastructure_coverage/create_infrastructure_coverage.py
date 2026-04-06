
import json
import math
import time

import requests
import psycopg2
import useful as u
ETA_MAX = 15
DIST_MATRIX_MAX_DEST = 10

def generalize_hex_tables(conn):
    cursor_s = conn.cursor()

    for suffix in ["", "_s", "_m", "_l", "_xl"]:
        gen_table = "hex_tiles" + suffix
        print(f"Started filling {gen_table} table")
        cursor = conn.cursor(name=f'hex_iterator_{gen_table}')
        cursor.itersize = 500
        cursor.execute(f"SELECT gid, ST_AsText(geometry) FROM {gen_table}")

        for i, row in enumerate(cursor.fetchall()):
            gid, geom = row

            cursor_s.execute(f" SELECT infrastructure"
                             f" FROM osm_buildings_poly WHERE"
                             f" ST_Intersects(geometry, 'SRID=3857;{geom}')")

            infr_arr = []

            for row_i in cursor_s.fetchall():
                infr = row_i[0]
                if infr is not None:
                    infr_arr.append(infr)

            if len(infr_arr) > 0:
                infr_arr.sort()
                infr_avg = infr_arr[int(len(infr_arr) / 2)]
            else:
                infr_avg = 0

            if i % 1000 == 0:
                print(f"{gen_table}, {i}")

            cursor_s.execute(f"UPDATE {gen_table} SET infrastructure = {infr_avg}"
                             f" WHERE gid = {gid}")

        conn.commit()


def get_coef_from_eta(eta):
    # eta is in [0, 15]
    rev_eta = ETA_MAX - eta + 1
    return rev_eta / ETA_MAX


def get_coef_variety(poi_types):
    return len(poi_types) / 5.0


def update_building_record(cursorQ, gid, infr):
    cursorQ.execute(f"UPDATE osm_buildings_poly"
                    f" SET infrastructure = {infr}"
                    f" WHERE id = {gid}")


def update_building_parts_records(conn, gid, infr):
    cursorN = conn.cursor()
    cursorM = conn.cursor()
    cursorN.execute(f"SELECT ST_AsText(geometry) from osm_buildings_poly where id = {gid}")
    geom_text = cursorN.fetchone()[0]

    cursorN.execute(f"SELECT id "
                    f" FROM osm_building_parts_poly "
                    f" WHERE is_drawable = 1 and ST_Intersects(geometry, 'SRID=3857;{geom_text}')")

    for row in cursorN.fetchall():
        pid = row[0]
        cursorM.execute(f"UPDATE osm_building_parts_poly"
                        f" SET infrastructure = {infr}"
                        f" WHERE id = {pid}")


def extract_coord_from_text(text):
    try:
        i_start = text.find('(')
        i_end = text.find(')')
        coord = text[i_start + 1:i_end]
        x, y = coord.split(' ')
        return float(x), float(y)
    except Exception as e:
        print("Exceptin in extract_coord_from_text():", e, text)
    return None, None

def extract_targets_from_raw(raw_targets):
    targets = []
    for raw_target in raw_targets:
        targets.append({"lat": raw_target["lat"], "lon": raw_target["lon"]})
    return targets


def get_source_to_targets(navigation_url: str, src_lat, src_lon, raw_targets):
    """Uses one-to-many request to distance matrix valhalla API:
    https://valhalla.readthedocs.io/en/latest/api/matrix/api-reference/
    """

    json_val = {
        "sources": [
            {"lat": src_lat, "lon": src_lon}
        ],
        "targets": extract_targets_from_raw(raw_targets),
        "costing": "pedestrian"
    }

    resp = requests.post(navigation_url, json=json_val)
    return resp.json()


def handle_source_to_targets(routing_resp, poi_types, destinations):
    infrastructure_val = 0
    if "sources_to_targets" not in routing_resp:
        print(f"Error fetching source to targets: {routing_resp}")
        return infrastructure_val

    assert len(routing_resp["sources_to_targets"]) == 1
    
    for item in routing_resp["sources_to_targets"][0]:
        if "time" not in item or item["time"] is None:
            print(f"no time in response: {routing_resp}")
            continue

        eta = int(math.floor(item["time"] / 60.0))
        if eta > ETA_MAX:
            continue

        eta_coef = get_coef_from_eta(eta)
        i = item["to_index"]
        infrastructure_val += destinations[i]["importance"] * eta_coef
        poi_types.add(destinations[i]["poi_type"])

    
    destinations.clear()
    return infrastructure_val


def calc_infrastructure(conn, navigation_url: str):
    """
    Рассчитывает показатель инфраструктурной доступности для зданий на основе близости к POI (точкам интереса).
    Для каждого здания:
    1. Находит все POI в пределах буферной зоны.
    2. Запрашивает время/расстояние до них через сервис маршрутизации.
    3. Вычисляет общий показатель инфраструктуры с учетом важности и разнообразия POI.
    4. Сохраняет результат в БД.

    Args:
        conn: соединение с PostgreSQL/PostGIS
        navigation_url: URL API маршрутизации (например, OSRM, GraphHopper)
    """

    # Создаем курсоры для работы с БД:
    # - основной курсор для выборки зданий (с именем для управления памятью)
    # - cursorA для обновления записей зданий
    # - cursorH для поиска POI в буфере здания
    cursor = conn.cursor(name='buildings_infr_iterator')
    cursor.itersize = 300  # Оптимизация: выборка по 300 записей за раз
    cursorA = conn.cursor()
    cursorH = conn.cursor()

    # SQL-запрос для выборки зданий:
    # - id, is_drawable (флаг, состоит ли здание из частей)
    # - буферная зона вокруг здания (в метрах, преобразованная в WKT-текст)
    # - центр здания (в WGS84, для маршрутизации)
    cursor.execute(f" SELECT"
                   f"   id, is_drawable, ST_AsText(buffer), ST_AsText(ST_Transform(center, 4326)) "
                   f" FROM"
                   f"   (SELECT"
                   f"       id, is_drawable, ST_Centroid(geometry) as center,"
                   f"       ST_Buffer(geometry, {u.INFRASTRUCTURE_DIST_M} * coef) as buffer"
                   f"    FROM "
                   f" (SELECT id, is_drawable, geometry, {u.QUERY_COEF} as coef FROM"
                   f" osm_buildings_poly) as q_inner) as q")

    print("Fetching buildings geometry: retrieved the cursor")

    # Обрабатываем каждое здание
    for i, rec in enumerate(cursor.fetchall()):
        gid, is_drawable, buffer_text, center_text = rec

        # Извлекаем координаты центра здания (широта, долгота)
        bld_lon, bld_lat = extract_coord_from_text(center_text)
        if bld_lon is None or bld_lat is None:
            continue  # Пропускаем здания с некорректными координатами

        # Ищем POI, попадающие в буферную зону здания
        cursorH.execute(f"SELECT poi_type, importance, ST_AsText(ST_Transform(geometry, 4326))"
                        f" FROM infrastructure_poi"
                        f" WHERE ST_Intersects(geometry, 'SRID=3857;{buffer_text}')")

        infrastructure_val = 0.0  # Общий показатель инфраструктуры
        poi_types = set()  # Множество типов POI (для учета разнообразия)
        destinations = []  # Список POI для маршрутизации

        # Обрабатываем все найденные POI
        for rec_infr in cursorH.fetchall():
            poi_type, importance, poi_center_text = rec_infr
            poi_lon, poi_lat = extract_coord_from_text(poi_center_text)

            # Добавляем POI в список для маршрутизации
            destinations.append({
                "lat": poi_lat, 
                "lon": poi_lon, 
                "poi_type": poi_type, 
                "importance": importance
            })

            # Если набралось максимальное количество POI для одного запроса,
            # отправляем запрос в API маршрутизации и обрабатываем результат
            if len(destinations) == DIST_MATRIX_MAX_DEST:
                routing_resp = get_source_to_targets(navigation_url, bld_lat, bld_lon, destinations)
                infrastructure_val += handle_source_to_targets(routing_resp, poi_types, destinations)
                destinations.clear()  # Очищаем список после обработки

        # Обрабатываем оставшиеся POI (если их меньше DIST_MATRIX_MAX_DEST)
        if destinations:
            routing_resp = get_source_to_targets(navigation_url, bld_lat, bld_lon, destinations)
            infrastructure_val += handle_source_to_targets(routing_resp, poi_types, destinations)
            destinations.clear()

        # Корректируем показатель с учетом разнообразия POI
        infrastructure_val *= get_coef_variety(poi_types)

        # Логирование прогресса (каждые 100к зданий)
        if i % 100000 == 0:
            print(f"Calculated infrastructure value for {i} buildings")

        # Обновляем запись здания в БД
        update_building_record(cursorA, gid, infrastructure_val)

        # Если здание состоит из частей, обновляем и их
        if is_drawable is not None:
            update_building_parts_records(conn, gid, infrastructure_val)

    # Фиксируем все изменения в БД
    conn.commit()

def create_coverage(database_url: str, navigation_url: str):
    print("Начало создания слоя инфраструктуры")
    conn = psycopg2.connect(database_url)
    print("Подключение к БД")

    tic = time.perf_counter()

    #calc_infrastructure(conn, navigation_url + "/sources_to_targets")
    print("Calculated infrastructure for buildings.")

    generalize_hex_tables(conn)
    print("Generalized infrastructure impact for hexes.")

    conn.close()

    toc = time.perf_counter()
    print(f"Finished creating infrastructure coverage in {toc - tic:0.1f} s")


if __name__ == "__main__":
    create_coverage()
