from collections import defaultdict
from typing import Dict
from typing import List

from shapely import wkt
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from tqdm import tqdm
from Loader.Loader.Entities.HexagonSize import HexagonSize
from Loader.Loader.Entities.City import City   
from Loader.Loader.Entities.SetElement import SetElement
from Loader.Loader.Entities.EcologyHexagon import EcologyHexagon
from Loader.Loader.Services.Utils import to_meters
from Loader.Loader.Phases.create_ecology_coverage.impact import get_impact_by_city_type, get_impact_by_population
from Loader.Loader.Phases.create_ecology_coverage.internal import EcologyPOI, Road



def get_settlements_inside_polygon(
        connection,
        polygon_wgs84: Polygon,
        scale_factor: float
) -> List[SetElement]:
    settlements = []
    with connection.cursor() as cursor:
        query = f"""
            SELECT 
                ST_AsText(ST_Transform(geometry, 4326)), 
                population,
                type
            FROM public.osm_place_poly
            WHERE ST_Intersects(geometry,
                ST_Transform(
                    'SRID=4326;{polygon_wgs84.wkt}', 3857
                )
             )
        """
        cursor.execute(query)
        for (wkt_polygon, population, city_type) in cursor.fetchall():
            polygon = wkt.loads(wkt_polygon)
            _, polygon = to_meters(polygon, scale_factor=scale_factor)
            city_type_impact = get_impact_by_city_type(city_type)
            population_impact = get_impact_by_population(population)
            if isinstance(polygon, Polygon):
                settlements.append(
                    SetElement(
                        polygon=polygon,
                        city_type=city_type,
                        city_type_impact=city_type_impact,
                        population=population,
                        population_impact=population_impact
                    )
                )
            elif isinstance(polygon, MultiPolygon):
                for geometry in polygon.geoms:
                    settlements.append(
                        SetElement(
                            polygon=geometry,
                            city_type=city_type,
                            city_type_impact=city_type_impact,
                            population=population,
                            population_impact=population_impact
                        )
                    )
            else:
                print(f"Settlements: Unsupported type of geometry: {type(polygon)}. Skip.")

    return settlements


def get_roads_inside_polygon(connection, polygon_wgs84: Polygon, scale_factor: float) -> List[Road]:
    roads = []
    with connection.cursor() as cursor:
        query = f"""
            SELECT
                ST_AsText(
                    ST_Intersection(
                        ST_Transform(geometry, 4326),
                        'SRID=4326;{polygon_wgs84.wkt}'
                    )
                ) as road, 
                type as road_type
            FROM public.osm_roads_way 
            WHERE
                type not in ('service', 'track', 'raceway', 'runway')
                and ST_Intersects(geometry, ST_Transform('SRID=4326;{polygon_wgs84.wkt}', 3857))
        """
        cursor.execute(query)
        for (wkt_linestring, road_type) in cursor.fetchall():
            line = wkt.loads(wkt_linestring)
            _, line = to_meters(line, scale_factor=scale_factor)
            if isinstance(line, LineString):
                roads.append(
                    Road(
                        road_type=road_type,
                        line=line
                    )
                )
            elif isinstance(line, MultiLineString):
                for geometry in line.geoms:
                    roads.append(
                        Road(
                            road_type=road_type,
                            line=geometry
                        )
                    )
            else:
                print(f"Roads: Unsupported type of geometry: {type(line)}. Skip.")

    return roads


def get_ecology_pois_inside_polygon(
        connection,
        polygon_wgs84: Polygon,
        scale_factor: float
) -> List[EcologyPOI]:
    ecology_pois = []
    with connection.cursor() as cursor:
        query = f"""
            SELECT
                ST_AsText(ST_Transform(geometry_poly, 4326)),
                impact
            FROM
                public.ecology_poi
            WHERE 
                impact > 0 
                and ST_Intersects(geometry_poly, ST_Transform('SRID=4326;{polygon_wgs84.wkt}', 3857))
        """
        cursor.execute(query)
        for (wkt_polygon, impact) in cursor.fetchall():
            polygon = wkt.loads(wkt_polygon)
            _, polygon = to_meters(polygon, scale_factor=scale_factor)
            if isinstance(polygon, Polygon):
                ecology_pois.append(
                    EcologyPOI(
                        impact=impact,
                        polygon=polygon
                    )
                )
            elif isinstance(polygon, MultiPolygon):
                for geometry in polygon:
                    ecology_pois.append(
                        EcologyPOI(
                            impact=impact,
                            polygon=geometry
                        )
                    )
            else:
                print(f"Ecology POI: Unsupported type of geometry: {type(polygon)}. Skip.")

    return ecology_pois


def get_forests_inside_polygon(connection, polygon_wgs84: Polygon, scale_factor: float) -> List[Polygon]:
    forests = []
    with connection.cursor() as cursor:
        query = f"""
            SELECT
                ST_AsText(ST_Intersection(ST_Transform(geometry, 4326), 'SRID=4326;{polygon_wgs84.wkt}'))
            FROM 
                public.osm_natural_poly
            WHERE 
                ST_Intersects(geometry, ST_Transform('SRID=4326;{polygon_wgs84.wkt}', 3857))
        """
        cursor.execute(query)
        for (wkt_polygon,) in cursor.fetchall():
            polygon = wkt.loads(wkt_polygon)
            _, polygon = to_meters(polygon, scale_factor=scale_factor)
            if isinstance(polygon, Polygon):
                forests.append(polygon)
            elif isinstance(polygon, MultiPolygon):
                for geometry in polygon.geoms:
                    forests.append(geometry)
            else:
                print(f"Forests: Unsupported type of geometry: {type(polygon)}. Skip.")

    return forests


def save_hexagons(connection, hexagons: List[EcologyHexagon]) -> None:
    rows_per_chunk = 1000
    hexagons_size_to_table_name: Dict[HexagonSize, str] = {
        HexagonSize.base: 'hex_tiles',
        HexagonSize.s: 'hex_tiles_s',
        HexagonSize.m: 'hex_tiles_m',
        HexagonSize.l: 'hex_tiles_l',
        HexagonSize.xl: 'hex_tiles_xl',
        HexagonSize.xxl: 'hex_tiles_xxl',
        HexagonSize.xxxl: 'hex_tiles_xxxl',
        HexagonSize.xxxxl: 'hex_tiles_xxxxl',
        HexagonSize.xxxxxl: 'hex_tiles_xxxxxl',
    }

    hexagons_size_to_hexagons: Dict[HexagonSize, List[EcologyHexagon]] = defaultdict(list)
    for hexagon in hexagons:
        hexagons_size_to_hexagons[hexagon.hexagon_size].append(hexagon)

    with connection.cursor() as cursor:
        for hexagon_size, hexagons in hexagons_size_to_hexagons.items():
            n_chunks = len(hexagons) // rows_per_chunk
            chunks = (hexagons[i:i + rows_per_chunk] for i in range(0, len(hexagons), rows_per_chunk))
            for chunk in tqdm(chunks, desc='Saving ecology hexagons', total=n_chunks):
                data = [
                    (
                        hexagon.impact,
                        f"SRID=3857;{hexagon.polygon_web_mercator.wkt}"
                    )
                    for hexagon in chunk
                ]

                args_str = ','.join(['%s'] * len(data))
                sql = f"INSERT INTO public.{hexagons_size_to_table_name[hexagon_size]} " \
                      "(impact, geometry) VALUES {}".format(args_str)
                cursor.execute(cursor.mogrify(sql, data))

    connection.commit()
