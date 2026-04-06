import psycopg2
import time

IS_UPDATED = "updated"
IS_DELETED = "deleted"
IS_NOT_UPDATED = "not updated"


def get_water_ids(conn, water_table, islands_table):
    cursor = conn.cursor(name=f'water_poly_cursor_{water_table}')
    cursor.itersize = 1000
    ids = {}

    cursor.execute(f" SELECT {water_table}.id, {islands_table}.id FROM {water_table}"
                   f" JOIN {islands_table} on"
                   f" ST_Intersects({water_table}.geometry, {islands_table}.geometry)")

    for row in cursor.fetchall():
        water_id, island_id = row

        if water_id not in ids:
            ids[water_id] = set()
        ids[water_id].add(island_id)

    return ids


def update_water_tables(conn, w_id, island_ids, water_table, islands_table):
    cursor = conn.cursor()
    cursor_upd = conn.cursor()

    res_val = IS_NOT_UPDATED

    while len(island_ids) > 0:
        for island_id in island_ids:
            cursor.execute(f"SELECT"
                           f" ST_AsText(ST_Difference(ST_MakeValid({water_table}.geometry), {islands_table}.geometry)),"
                           f" ST_IsEmpty(ST_Difference(ST_MakeValid({water_table}.geometry), {islands_table}.geometry))"
                           f" FROM {water_table}"
                           f" JOIN {islands_table} on"
                           f" {water_table}.id = {w_id} and {islands_table}.id = {island_id}"
                           f" and ST_Intersects(ST_MakeValid({water_table}.geometry), {islands_table}.geometry)")

            for row in cursor.fetchall():
                geom_text, is_empty = row
                if is_empty is True:
                    cursor_upd.execute(f"DELETE FROM {water_table} where id = {w_id}")
                    conn.commit()
                    return IS_DELETED

                cursor_upd.execute(f"UPDATE {water_table} SET"
                                   f" geometry = ST_MakeValid('SRID=3857;{geom_text}')"
                                   f" WHERE id = {w_id}")
                conn.commit()
                island_ids.remove(island_id)
                res_val = IS_UPDATED
                break
            break

    return res_val


def change_water(database_url: str):
    print("Started fixing water")
    conn = psycopg2.connect(database_url)
    tic = time.perf_counter()
    tables = [["osm_natural_water_poly", "osm_islands_poly"],
              ["osm_natural_water_gen2", "osm_islands_gen2"],
              ["osm_natural_water_gen1", "osm_islands_gen1"],
              ["osm_natural_water_gen0", "osm_islands_gen0"]]

    for tables_pair in tables:
        water_table, islands_table = tables_pair
        print(f"Handling {water_table} and {islands_table}")

        ids = get_water_ids(conn, water_table, islands_table)
        print(f"\tFound {len(ids)} water objects with islands.")

        res_vals = {}

        for w_id, island_ids in ids.items():
            res_val = update_water_tables(conn, w_id, island_ids, water_table, islands_table)
            if res_val not in res_vals:
                res_vals[res_val] = 0
            res_vals[res_val] += 1

        for res_val, count in res_vals.items():
            print(f"\t{res_val}: {count} water objects")

    if conn:
        conn.close()
    toc = time.perf_counter()

    print(f"Finished fixing water in {toc - tic:0.1f} s")


if __name__ == "__main__":
    database_url = ""
    change_water(database_url)
