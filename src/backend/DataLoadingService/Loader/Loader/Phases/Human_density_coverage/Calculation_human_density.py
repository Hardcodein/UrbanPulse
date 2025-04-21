import psycopg2
import json
import time


from Loader.Phases.Human_density_coverage.Calculation_roads_and_water_area import get_area_roads, get_area_rails, get_area_water
from Loader.Phases.Human_density_coverage.Helpers_human_density import get_rail_width,coordinants_from_text
import Loader.Phases.Human_density_coverage.Consts_human_density as Const_human_density


def calculation_humans_in_buildings(
    connection, 
    cursor, 
    area_land_text, 
    
    
):
    """
    Оценивает количество жителей в зданиях внутри заданной области.
    
    Параметры:
    - conn: соединение с БД
    - cursor: курсор БД
    - area_land_text: геометрия области в формате WKT (SRID 3857)
    - residents_per_apartment: среднее число жителей на квартиру (по умолчанию 2.5)
    - apartment_area: средняя площадь одной квартиры в м² (по умолчанию 50)
    
    Возвращает:
    - total_residents: общее количество жителей
    - buildings_with_data: количество зданий с данными по этажам
    - buildings_without_data: количество зданий без данных по этажам
    """
    residents_coef_apartment=2.5, 

    table = "osm_buildings_poly"
    
    cursor.execute(
        f"""
        SELECT 
            id,
            ST_Area(ST_Intersection(geometry, 'SRID=3857;{area_land_text}')) as area,
            building_levels,
            building_flats,
        FROM {table}
        WHERE ST_Intersects(geometry, 'SRID=3857;{area_land_text}')
        """
    )
    
    total_residents = 0.0

    buildings_with_data = 0

    buildings_without_data = 0
    
    buildings_with_levels = []
    
    for rec in cursor.fetchall():

        gid, area, levels,flats = rec
        
        if area <= 0:
            continue  
            
        if levels is not None:
            
            # Оценка количества квартир в здании:
            # (площадь здания / площадь одной квартиры) * число этажей
            residents = int(flats) * residents_coef_apartment
            
            total_residents += residents
            buildings_with_data += 1
            buildings_with_levels.append(residents)
        else:
            buildings_without_data += 1
    
    # Если есть здания без данных по этажам, используем среднее значение от зданий с данными
    if buildings_without_data > 0 and buildings_with_data > 0:
        avg_residents_per_building = sum(buildings_with_levels) / buildings_with_data
        total_residents += avg_residents_per_building * buildings_without_data
    
    return {
        "total_residents": total_residents,
        "buildings_with_data": buildings_with_data,
        "buildings_without_data": buildings_without_data,
    }

def update_building_human_density_record(cursorQ, gid, pct_human_density):
    cursorQ.execute(f"UPDATE osm_buildings_poly"
                    f" SET pct_human_density = {pct_human_density}"
                    f" WHERE id = {gid}")


def update_building_parts_human_denstity_records(conn, gid, pct_human_density):
    cursorN = conn.cursor()
    cursorM = conn.cursor()
    cursorN.execute(f"SELECT ST_AsText(geometry) from osm_buildings_poly where id = {gid}");
    geom_text = cursorN.fetchone()[0]

    cursorN.execute(f"SELECT id "
                    f" FROM osm_building_parts_poly "
                    f" WHERE is_drawable = 1 and ST_Intersects(geometry, 'SRID=3857;{geom_text}')")

    for row in cursorN.fetchall():
        pid = row[0]
        cursorM.execute(f"UPDATE osm_building_parts_poly"
                        f" SET pct_human_density = {pct_human_density}"
                        f" WHERE id = {pid}")


def generalize_hex_human_density_tables(conn):
    cursor_s = conn.cursor()

    for suffix in ["", "_s", "_m", "_l", "_xl"]:

        gen_table = "hex_tiles" + suffix
        print(f"Started filling {gen_table} table")
        cursor = conn.cursor(name=f'hex_iterator_{gen_table}')
        cursor.itersize = 500
        cursor.execute(f"SELECT gid, ST_AsText(geometry) FROM {gen_table}")

        for item, row in enumerate(cursor.fetchall()):
            gid, geom = row

            cursor_s.execute(f" SELECT pct_human_density, "
                             f" ST_Area(ST_Intersection(geometry, 'SRID=3857;{geom}'))"
                             f" FROM osm_buildings_poly WHERE"
                             f" ST_Intersects(geometry, 'SRID=3857;{geom}')")

            gen_pct_bld_human_density = 0.0
            area_pct = 0.0

            for row_i in cursor_s.fetchall():
                
                pct_bld_human_density, area_bld = row_i

                if pct_bld_human_density is not None and pct_bld_human_density > 0.0:
                    gen_pct_bld_human_density += float(pct_bld_human_density) * area_bld
                    area_pct += area_bld

            if gen_pct_bld_human_density > 0:
                gen_pct_bld_human_density = gen_pct_bld_human_density / area_pct

            if item % 1000 == 0:
                print(f"{gen_table}, {item}")

            cursor_s.execute(f"UPDATE {gen_table} SET bld_human_density = {gen_pct_bld_human_density} "
                             f" WHERE gid = {gid}")

        conn.commit()

def calculation_and_update_human_density(connection):
    cursor = connection.cursor(name='buildings_iterator')
    cursor.itersize = 100
    cursorA = connection.cursor()

    # Получаем здания с буферными зонами
    cursor.execute(f"""
        SELECT
            id, building_levels, is_drawable, 
            ST_AsGeoJSON(buffer), ST_AsText(buffer), ST_Area(buffer),
            coef
        FROM (
            SELECT
                id, building_levels, is_drawable, geometry, coef,
                ST_Buffer(geometry, {Const_human_density.NEIGHBOURS_DIST_METERES} * coef) as buffer
            FROM (
                SELECT 
                    id, building_levels, is_drawable, geometry, 
                    {Const_human_density.QUERY_COEF} as coef 
                FROM osm_buildings_poly
            ) as q_inner
        ) as q
    """)

    print("Fetching buildings geometry: retrieved the cursor")

    for idx, rec in enumerate(cursor):
        gid, levels_count, is_drawable, buffer_text, buffer_plaintext, buffer_area, coef = rec
        
        # Пропускаем здания с некорректной площадью буфера
        if buffer_area is None or buffer_area <= 0:
            continue

        # Рассчитываем количество жителей в буферной зоне
        residents_data = calculation_humans_in_buildings(connection, cursorA, buffer_plaintext)

        total_residents_in_area = residents_data['total_residents']
        
        # Получаем площади дорог и водных объектов
        area_roads = get_area_roads(connection, cursorA, buffer_plaintext, coef)
        area_rails = get_area_rails(connection, cursorA, buffer_plaintext, coef)
        area_water = get_area_water(cursorA, buffer_plaintext)
        
        # Рассчитываем доступную для жилья площадь
        area_total = buffer_area
        area_inhabitable = area_total - area_roads - area_rails - area_water
        
        # Проверка корректности данных
        if area_inhabitable <= 0 or area_total <= 0:
            print(f"ERROR IN AREA CALCULATION: id = {gid}, "
                  f"total area = {area_total}, "
                  f"inhabitable area = {area_inhabitable}")
            continue

        # Рассчитываем плотность населения (чел/км²)
        human_density = (total_residents_in_area / area_inhabitable) * 100 if area_inhabitable > 0 else 0
        
        # Логирование прогресса
        if idx % 1000 == 0:
            print(f"Processed {idx} buildings, current density: {human_density:.2f} people/km²")

        # Обновляем запись здания
        update_building_human_density_record(cursorA, gid, human_density)

        # Если здание состоит из частей, обновляем и их
        if is_drawable is not None:
            update_building_parts_human_denstity_records(connection, gid, human_density)

    connection.commit()
    print("Human density calculation completed")

    
def calculation_human_denstity(database_url_string: str):

    connection = psycopg2.connect(database_url_string)

    print("Подключение к БД")

    tic = time.perf_counter()

    calculation_and_update_human_density(connection)

    generalize_hex_human_density_tables(connection)

    if connection:
        connection.close()

    toc = time.perf_counter()

    print(f"Конец расчета плотности населениия за --- {toc - tic:0.1f} s")


if __name__ == "__main__":
    calculation_human_denstity()
