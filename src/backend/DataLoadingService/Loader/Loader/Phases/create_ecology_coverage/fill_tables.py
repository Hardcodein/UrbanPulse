import psycopg2
import time
import json
import math
import dateutil.parser as parser
import useful as u

IMPACT_K = u.HEX_R * 2.0 / u.ECOLOGY_LINE_SEGMENT_LEN_M

IMPACT_EXCEPTIONAL = 2050 * IMPACT_K
IMPACT_MAX = 1920 * IMPACT_K
IMPACT_VERY_HIGH = 1020 * IMPACT_K
IMPACT_HIGH = 1680 * IMPACT_K
IMPACT_AVG = 540 * IMPACT_K
IMPACT_LOW = 240 * IMPACT_K
IMPACT_NONE = 0


def coords_from_text(text):
    obj = json.loads(text)
    assert obj["type"] == "Point"
    return obj["coordinates"]


def coords_too_close(c1, c2, coef):
    MIN_DIST = 500.0 * coef
    dist = math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)
    return dist < MIN_DIST


def get_powerplant_impact(s):
    s = s.lower().strip()
    if len(s) < 3 or s.find("котельн") != -1 or s.find("подстанц") != -1:
        return IMPACT_NONE

    if s.find("район") != -1 or s.find("квартал") != -1 or s == "тэц":  # ртс
        return IMPACT_AVG

    return IMPACT_VERY_HIGH


def is_factory(s):
    s = s.lower().strip()
    keywords = ["завод", "з-д", "комбинат", "фабрика", "заготов", "производст", "пилорам", "мануфактур",
                "лесопилк", "цех", "пекарн", "ферма", "нпц", "нефте", "промышл", "предприят", "цбк", "перераб"]
    for keyword in keywords:
        if s.find(keyword) != -1:
            return True
    return False


def is_not_factory(s):
    s = s.lower().strip()
    keywords = ["электродепо", "депо ", "недостроен", "заброшен", "бывшая", "бывший", "бывшее", "бывшие"]
    for keyword in keywords:
        if s.find(keyword) != -1:
            return True
    return False


def get_factory_impact(s):
    s = s.lower().strip()

    keywords_bad = ["мусор", "нефте"]
    for keyword in keywords_bad:
        if s.find(keyword) != -1:
            return IMPACT_EXCEPTIONAL

    keywords = ["мясо", "мясн", "бетон", "асфальт", "цемент", "кокс", "очист", "цбк", "целлюлоз"]
    for keyword in keywords:
        if s.find(keyword) != -1:
            return IMPACT_VERY_HIGH

    return IMPACT_LOW


def get_energy_sources(s):
    translations = {
        'gas': 'природный газ',
        'nuclear': 'ядерная',
        'hydro': 'вода',
        'coal': 'уголь',
        'oil': 'мазут',
        'fossil': 'мазут'
    }
    sources = []
    for item in s.split(';'):
        item = item.lower().strip()
        if item not in translations:
            if len(item) > 0:
                print(f"WARNING: {item} NOT IN ENERGY SOURCE TRANSLATIONS.")
            continue
        sources.append(translations[item])

    return ', '.join(sources)


def remove_quotes(s):
    return s.replace('\'', "")


def get_airport_type_impact(s1, s2):
    translations = {
        'public': ['гражданский', IMPACT_HIGH],
        'international': ['междунородный', IMPACT_MAX],
        'regional': ['междугородний', IMPACT_MAX],
        'private': ['частный', IMPACT_AVG],
        'airfield': ['взлетное поле', IMPACT_AVG],
        'military': ['военный', IMPACT_AVG],
        'military/public': ['гражданский, военный', IMPACT_HIGH],
        'gliding': ['для планёров', IMPACT_AVG]
    }

    res = ['гражданский', IMPACT_AVG]

    for s in [s1, s2]:
        s = s.lower().strip()

        if s in translations:
            if translations[s][1] >= res[1]:
                res = translations[s]

    return res


def get_year(s):
    date_time = parser.parse(s)
    return str(date_time.year)


def get_url_simple(url1, url2):
    if len(url1) > 0:
        return url1
    if len(url1) > 0:
        return url2
    return ""


def get_url(url_wiki, url1, url2):
    if len(url_wiki) > 0:
        pref, objname = url_wiki.split(":")
        return "https://{}.wikipedia.org/wiki/{}".format(pref, objname)

    return get_url_simple(url1, url2)


def update_if_empty(d, key, new_val):
    if d[key] is None or len(d[key]) == 0:
        d[key] = new_val


def fill_powerplants(conn):
    cursor = conn.cursor(name='powerplants_cursor')
    cursorI = conn.cursor()
    cursor.itersize = 300

    objects = {}

    cursor.execute(f"SELECT name, name_en, name_ru, operator, start_date, plant_source,"
                   f" wikipedia, contact_website, website,"
                   f" ST_AsText(geometry), ST_AsText(ST_Centroid(geometry)), ST_AsGeoJSON(ST_Centroid(geometry)),"
                   f" ST_Area(geometry), {u.QUERY_COEF} as coef"
                   f" FROM osm_powerplants_poly WHERE name <> '' UNION ALL"
                   f" SELECT name, name_en, name_ru, operator, start_date, plant_source,"
                   f" wikipedia, contact_website, website, ST_AsText(geometry), ST_AsText(ST_Centroid(geometry)),"
                   f" ST_AsGeoJSON(ST_Centroid(geometry)),"
                   f" ST_Area(geometry), {u.QUERY_COEF} as coef"
                   f" FROM osm_powerplants_line WHERE name <> ''")

    for row in cursor.fetchall():
        name, name_en, name_ru, operator, \
        start_date_text, plant_source, wikipedia, contact_website, website, \
        geom, center, center_json, area, coef = row

        start_year = ""
        if len(start_date_text) > 3:
            year = get_year(start_date_text)
            if len(year) == 4:
                start_year = year

        energy_source = ""

        if len(plant_source) > 0:
            energy_source = get_energy_sources(plant_source)

        impact = get_powerplant_impact(name)
        if plant_source.lower().strip() in ('hydro', 'wind', 'solar', 'geothermal'):
            impact = 0

        if plant_source is None or len(plant_source) == 0 and name.lower().find("гэс") != -1:
            impact = 0

        url = get_url(wikipedia, contact_website, website)

        coord = coords_from_text(center_json)

        if name in objects:
            if coords_too_close(coord, objects[name]["center"], coef):
                continue

            update_if_empty(objects[name], "operator", operator)

            update_if_empty(objects[name], "name_en", name_en)
            update_if_empty(objects[name], "name_ru", name_ru)

            update_if_empty(objects[name], "start_year", start_year)
            update_if_empty(objects[name], "energy_source", energy_source)
            update_if_empty(objects[name], "url", url)

            if objects[name]["impact"] < impact:
                objects[name]["impact"] = impact

            if area > objects[name]["area"]:
                objects[name]["center"] = coord
                objects[name]["center_geom"] = center
                objects[name]["geom"] = geom
                objects[name]["area"] = area

        else:
            objects[name] = {
                "center": coord,
                "center_geom": center,
                "geom": geom,
                "area": area,
                "operator": operator,
                "name_en": name_en,
                "name_ru": name_ru,
                "start_year": start_year,
                "energy_source": energy_source,
                "url": url,
                "impact": impact
            }

    for name, data in objects.items():
        cursorI.execute(f"INSERT INTO ecology_poi (poi_type, title, title_en, title_ru, operator, "
                        f"start_year, energy_source, url, "
                        f"impact, geometry, geometry_poly) VALUES ('powerplant', '{remove_quotes(name)}', "
                        f"'{remove_quotes(data['name_en'])}', '{remove_quotes(data['name_ru'])}',"
                        f"'{remove_quotes(data['operator'])}', "
                        f"'{data['start_year']}',"
                        f"'{data['energy_source']}', '{data['url']}', {data['impact']}, "
                        f"'SRID=3857;{data['center_geom']}', 'SRID=3857;{data['geom']}')")

    conn.commit()


def fill_factories(conn):
    cursor = conn.cursor(name='factories_cursor')
    cursorI = conn.cursor()
    cursor.itersize = 300

    objects = {}

    cursor.execute(f"SELECT name, name_ru, name_en, operator, owner, man_made, industrial, factory, product, contact_website, website, "
                   f"ST_AsText(ST_Centroid(geometry)), ST_AsGeoJSON(ST_Centroid(geometry)),"
                   f"ST_AsText(geometry), ST_Area(geometry), {u.QUERY_COEF} as coef "
                   f"FROM osm_factories_poly  WHERE name <> '' and (power is null or power = '') UNION ALL "
                   f"SELECT  name, name_ru, name_en, operator, owner, man_made, industrial, factory, product, contact_website, website, "
                   f"ST_AsText(ST_Centroid(geometry)), ST_AsGeoJSON(ST_Centroid(geometry)),"
                   f"ST_AsText(geometry), ST_Area(geometry), {u.QUERY_COEF} as coef "
                   f"FROM osm_factories_line WHERE name <> '' and (power is null or power = '')")

    for row in cursor.fetchall():
        name, name_ru, name_en, operator, owner, man_made, industrial, factory, product, contact_website, \
        website, center, center_json, geom, area, coef = row

        rec_is_factory = man_made == "works" or man_made == "wastewater_plant" or man_made == "factory" or \
                         len(industrial) > 0

        if not rec_is_factory:
            rec_is_factory = is_factory(name)

        if is_not_factory(name):
            continue

        if not rec_is_factory:
            continue

        if len(industrial) > 0 and industrial not in ["slaughterhouse", "bakery", "asphalt_plant",
                                                      "water_filters", "manufacture", "plastic",
                                                      "brewery", "factory"]:
            continue

        impact = get_factory_impact(name)
        url = get_url_simple(contact_website, website)

        coord = coords_from_text(center_json)

        if name in objects:
            if coords_too_close(coord, objects[name]["center"], coef):
                continue

            update_if_empty(objects[name], "operator", operator)
            update_if_empty(objects[name], "owner", owner)
            update_if_empty(objects[name], "product", product)
            update_if_empty(objects[name], "url", url)
            update_if_empty(objects[name], "name_ru", name_ru)
            update_if_empty(objects[name], "name_en", name_en)

            if objects[name]["impact"] < impact:
                objects[name]["impact"] = impact

            if area > objects[name]["area"]:
                objects[name]["center"] = coord
                objects[name]["center_geom"] = center
                objects[name]["geom"] = geom
                objects[name]["area"] = area

        else:
            objects[name] = {
                "center": coord,
                "center_geom": center,
                "geom": geom,
                "area": area,
                "operator": operator,
                "owner": owner,
                "product": product,
                "url": url,
                "impact": impact,
                "name_en": name_en,
                "name_ru": name_ru
            }

    for name, data in objects.items():
        cursorI.execute(f"INSERT INTO ecology_poi (poi_type, title, title_en, title_ru, operator, owner, product, url, "
                        f"impact, geometry, geometry_poly) VALUES ('factory', '{remove_quotes(name)}', "
                        f"'{remove_quotes(data['name_en'])}', '{remove_quotes(data['name_ru'])}', "
                        f"'{remove_quotes(data['operator'])}', '{remove_quotes(data['owner'])}',"
                        f"'{data['product']}', '{data['url']}', {data['impact']}, 'SRID=3857;{data['center_geom']}', "
                        f"'SRID=3857;{data['geom']}')")

    conn.commit()


def fill_airports(conn):
    cursor = conn.cursor(name='airports_cursor')
    cursorI = conn.cursor()
    cursor.itersize = 300

    objects = {}
    cursor.execute(f"SELECT name, name_en, name_ru, operator, owner, aerodrome_type, aerodrome, wikipedia, contact_website, website, "
                   f"ST_AsText(geometry), ST_AsText(ST_Centroid(geometry)),"
                   f"ST_AsGeoJSON(ST_Centroid(geometry)), ST_Area(geometry), {u.QUERY_COEF} as coef "
                   f"FROM osm_airports_poly  UNION ALL "
                   f"SELECT  name, name_en, name_ru, operator, owner, aerodrome_type, aerodrome, wikipedia, contact_website, website,  "
                   f"ST_AsText(geometry), ST_AsText(ST_Centroid(geometry)), "
                   f"ST_AsGeoJSON(ST_Centroid(geometry)), ST_Area(geometry), {u.QUERY_COEF} as coef "
                   f"FROM osm_airports_line UNION ALL "
                   f"SELECT  name, name_en, name_ru, operator, owner, aerodrome_type, aerodrome, wikipedia, contact_website, website,  "
                   f"ST_AsText(geometry), ST_AsText(ST_Centroid(geometry)), "
                   f"ST_AsGeoJSON(ST_Centroid(geometry)), ST_Area(geometry), {u.QUERY_COEF} as coef "
                   f"FROM osm_airports_point"
                   )

    for row in cursor.fetchall():
        name, name_en, name_ru, operator, owner, aerodrome_type, aerodrome, wikipedia, contact_website, \
        website, geom, center, center_json, area, coef = row

        aero_type, impact = get_airport_type_impact(aerodrome_type, aerodrome)

        url = get_url(wikipedia, contact_website, website)

        coord = coords_from_text(center_json)

        if name in objects:
            if coords_too_close(coord, objects[name]["center"], coef):
                continue

            update_if_empty(objects[name], "operator", operator)
            update_if_empty(objects[name], "owner", owner)
            update_if_empty(objects[name], "aero_type", aero_type)
            update_if_empty(objects[name], "url", url)
            update_if_empty(objects[name], "name_en", name_en)
            update_if_empty(objects[name], "name_ru", name_ru)

            if objects[name]["impact"] < impact:
                objects[name]["impact"] = impact

            if area > objects[name]["area"]:
                objects[name]["center"] = coord
                objects[name]["center_geom"] = center
                objects[name]["geom"] = geom
                objects[name]["area"] = area

        else:
            objects[name] = {
                "center": coord,
                "center_geom": center,
                "geom": geom,
                "area": area,
                "operator": operator,
                "owner": owner,
                "aero_type": aero_type,
                "url": url,
                "impact": impact,
                "name_en": name_en,
                "name_ru": name_ru
            }

    for name, data in objects.items():
        cursorI.execute(f"INSERT INTO ecology_poi (poi_type, title, title_en, title_ru, operator, owner, poi_subtype, url, "
                        f"impact, geometry, geometry_poly) VALUES ('airport', '{remove_quotes(name)}', "
                        f"'{remove_quotes(data['name_en'])}', '{remove_quotes(data['name_ru'])}', "
                        f"'{remove_quotes(data['operator'])}', '{remove_quotes(data['owner'])}',"
                        f"'{data['aero_type']}', '{data['url']}', {data['impact']}, "
                        f"'SRID=3857;{data['center_geom']}', 'SRID=3857;{data['geom']}')")

    conn.commit()


def fill_ecology_poi_table(database_url: str):
    print("Started filling ecology_poi table")
    conn = psycopg2.connect(database_url)
    tic = time.perf_counter()

    fill_powerplants(conn)
    fill_factories(conn)
    fill_airports(conn)

    conn.close()

    toc = time.perf_counter()
    print(f"Finished filling ecology_poi table in {toc - tic:0.1f} s")

def create_ecology_tables(conn):
    cursor = conn.cursor()

    table = "ecology_poi"
    commands = [f"DROP TABLE IF EXISTS {table}",
            f"CREATE TABLE {table} (gid serial, poi_type text, poi_subtype text, "
            f"title text, title_en text, title_ru text, operator text, operator_en text, operator_ru text,"
            f"owner text, product text, note text, "
            f"start_year text, energy_source text, url text, impact int)",
            f"ALTER TABLE {table} ADD PRIMARY KEY (gid)",
            f"SELECT AddGeometryColumn('', '{table}', 'geometry', 3857, 'GEOMETRY', 2)",
            f"SELECT AddGeometryColumn('', '{table}', 'geometry_poly', 3857, 'GEOMETRY', 2)",
            f"CREATE INDEX {table}_geom_idx ON {table} USING GIST(geometry)",
            f"CREATE INDEX {table}_geom_poly_idx ON {table} USING GIST(geometry_poly)",
            ]

    for command in commands:
        cursor.execute(command)
        conn.commit()

if __name__ == "__main__":
    database_url = "postgresql://postgres:postgres_password@localhost:65432/maps_to_database"
    create_ecology_tables(psycopg2.connect(database_url))
    fill_ecology_poi_table(database_url)
