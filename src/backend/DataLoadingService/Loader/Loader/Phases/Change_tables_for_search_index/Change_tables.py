import psycopg2
import time


def change_tables_for_search_index(database_url_string: str):

    connection = psycopg2.connect(database_url_string)

    print("Подключение к БД")
    tic = time.perf_counter()

    cursor_upd = connection.cursor()
    cursor_upd.execute("INSERT INTO osm_place_poly SELECT * FROM osm_place_point")
    connection.commit()

    if connection:
        connection.close()
    toc = time.perf_counter()

    print(f"Окончена подготовка индексов {toc - tic:0.1f} s")


if __name__ == "__main__":
    change_tables_for_search_index()
