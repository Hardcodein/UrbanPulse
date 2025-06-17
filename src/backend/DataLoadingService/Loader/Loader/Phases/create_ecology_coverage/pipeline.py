import time
from pathlib import Path
from typing import Dict
from typing import List

import psycopg2
import pyproj as pyproj
from shapely.geometry import Polygon
from shapely.ops import transform
from shapely.geometry.base import BaseGeometry
from tqdm import tqdm

from Loader.Loader.Phases.create_ecology_coverage.database import get_ecology_pois_inside_polygon,get_forests_inside_polygon,get_roads_inside_polygon,get_settlements_inside_polygon
from Loader.Loader.Entities.HexagonSize import HexagonSize
from Loader.Loader.Services.Utils import get_available_cities,get_cell_centers,get_hexagons,to_degrees,get_centers_of_hexagons_inside_bounds,get_impact_grid_bounds,tranfrorm_grid_cells_to_web_mercator

from Loader.Loader.Phases.create_ecology_coverage.database import save_hexagons
from Loader.Loader.Phases.create_ecology_coverage.impact import compute_impact_value_in_grid_cells
from Loader.Loader.Phases.create_ecology_coverage.internal import ImpactParameters
from Loader.Loader.Entities.City import City
from Loader.Loader.Entities.Sector import Sector
from Loader.Loader.Entities.EcologyHexagon import EcologyHexagon
from Loader.Loader.Entities.ImpactGrid import ImpactGrid





def evaluate_impact_parameters(connection, sector: Sector) -> ImpactParameters:
    settlements = get_settlements_inside_polygon(connection, sector.ecology_polygon_wgs84, sector.scale_factor)
    roads = get_roads_inside_polygon(connection, sector.ecology_polygon_wgs84, sector.scale_factor)
    ecology_pois = get_ecology_pois_inside_polygon(connection, sector.ecology_polygon_wgs84, sector.scale_factor)
    forests = get_forests_inside_polygon(connection, sector.ecology_polygon_wgs84, sector.scale_factor)

    return ImpactParameters(
        settlements=settlements,
        roads=roads,
        ecology_pois=ecology_pois,
        forests=forests,
    )


def compute_impact_grid(
        sector: Sector,
        impact_parameters: ImpactParameters,
        ecology_r_m: float,
        grid_cell_side_m: float,
        segment_length_m: float
) -> ImpactGrid:
    grid = get_impact_grid_bounds(sector, grid_cell_side_m)
    compute_impact_value_in_grid_cells(grid, impact_parameters, ecology_r_m, segment_length_m)
    return grid


def get_sectors_by_city(city: City, sector_size_m: float, ecology_r_m: float) -> List[Sector]:
    sector_centers = get_cell_centers(city.polygon, sector_size_m)
    half_sector_m = sector_size_m / 2.
    sectors = []
    for (x, y) in sector_centers:
        left, bottom, right, top = x - half_sector_m, y - half_sector_m, x + half_sector_m, y + half_sector_m
        polygon = Polygon.from_bounds(left, bottom, right, top)
        if not city.polygon.intersects(polygon):
            continue

        # less vertices -> faster works
        ecology_polygon = Polygon.from_bounds(left, bottom, right, top).buffer(ecology_r_m, join_style=2, cap_style=3)
        sectors.append(
            Sector(
                scale_factor=city.scale_factor,
                polygon=polygon,
                polygon_wgs84=to_degrees(city.scale_factor, polygon),
                ecology_polygon_wgs84=to_degrees(city.scale_factor, ecology_polygon)
            )
        )
    return sectors


def generate_hexagons_by_polygon(
        polygon: Polygon,
        hexagon_edge_length_m: float
) -> List[Polygon]:
    sst = st = time.time()
    hexagon_centers = get_centers_of_hexagons_inside_bounds(*polygon.bounds, hexagon_edge_length_m)
    print(f'Centers: {time.time() - st}')
    st = time.time()
    hexagon_centers = [
        point
        for point in hexagon_centers
        if polygon.contains(point)
    ]
    print(f'Contains: {time.time() - st}')
    st = time.time()
    hexagons = get_hexagons(hexagon_centers, hexagon_edge_length_m)
    print(f'Single hexagon: {time.time() - st}')
    print(f'Total hexagon: {time.time() - sst}')
    return hexagons


def generate_hexagons_by_impact_grid_cells(
        city: City,
        sectors: List[Sector],
        impact_grids: List[ImpactGrid],
        hexagons_edge_lengths: Dict[HexagonSize, float]
) -> List[EcologyHexagon]:
    transformer = pyproj.Transformer.from_crs(pyproj.CRS(4326), pyproj.CRS(3857), always_xy=True)
    city_web_mercator = transform(transformer.transform, city.polygon_wgs84)

    mercator_grids, sectors_str_tree_inds, sectors_str_tree = tranfrorm_grid_cells_to_web_mercator(transformer, sectors, impact_grids)
    
    result = []
    for hexagon_size, hexagon_edge_length in hexagons_edge_lengths.items():
        st = time.time()
        print(f"Started generating hexagons geometry for {hexagon_size} sectors")
        hexagons = generate_hexagons_by_polygon(city_web_mercator, hexagon_edge_length)
        print(f"Finished generating hexagons geometry for {hexagon_size} sectors: {time.time() - st} sec")

        for i, hexagon in tqdm(
                enumerate(hexagons),
                total=len(hexagons),
                desc=f'Computing hexagons impact for {hexagon_size} sectors'
        ):
            sector_intersection_inds = []
            for cell in sectors_str_tree.query(hexagon):
    # Если это итерируемая коллекция (например, MultiPolygon или список)
                if hasattr(cell, '__iter__') and not isinstance(cell, BaseGeometry):
                    for subcell in cell:
                        geom = subcell if isinstance(subcell, BaseGeometry) else getattr(subcell, 'polygon', None)
                        if geom and isinstance(geom, BaseGeometry) and hexagon.intersects(geom):
                            index = sectors_str_tree_inds.get(id(subcell))
                            if index is not None:
                                sector_intersection_inds.append(index)
                else:
                # Одиночная геометрия или объект с polygon
                    geom = cell if isinstance(cell, BaseGeometry) else getattr(cell, 'polygon', None)
                    if geom and isinstance(geom, BaseGeometry) and hexagon.intersects(geom):
                        index = sectors_str_tree_inds.get(id(cell))
                        if index is not None:
                            sector_intersection_inds.append(index)
    
            total_impact = 0.
            for sector_index in sector_intersection_inds:
                grid = mercator_grids[sector_index]
                cell_intersection_inds = [
                    grid.str_tree_cells_inds[id(cell)]
                    for cell in grid.str_tree.query(hexagon)
                    if hexagon.intersects(cell)
                ]
                for cell_index in cell_intersection_inds:
                    cell = mercator_grids[sector_index].cells[cell_index]
                    total_impact += cell.impact * hexagon.intersection(cell.polygon).area / hexagon.area

            result.append(
                EcologyHexagon(
                    id=i,
                    impact=total_impact,
                    polygon_web_mercator=hexagon,
                    hexagon_size=hexagon_size
                )
            )

    return result


def create_ecology_coverage(
        database_url: str,
        hexagons_edge_sizes: Dict[HexagonSize, float],
        ecology_r_m: float,
        grid_cell_side_m: float,
        segment_length_m: float,
        sector_size_m: float,
        osm_dir: Path,
        cities: List[str]
) -> None:
    pipeline_start_time = time.time()
    print("Начало создания слоя экологии")

    connection = psycopg2.connect(database_url)

    with connection:
        available_cities: List[City] = get_available_cities(osm_dir, cities)
        total_amount_of_cities = len(available_cities)
        for i, city in enumerate(available_cities, start=1):
            st = time.time()
            print(f"***** Город `{city.name.upper()}`: {i} / {total_amount_of_cities}")

            sectors = get_sectors_by_city(city, sector_size_m, ecology_r_m)
            impact_parameters = [
                evaluate_impact_parameters(connection, sector)
                for sector in tqdm(sectors, desc=f'Evaluating impact parameters for {city.name} sectors')
            ]
            impact_grids = [
                compute_impact_grid(sector, impact_params, ecology_r_m, grid_cell_side_m, segment_length_m)
                for sector, impact_params in tqdm(
                    zip(sectors, impact_parameters),
                    total=len(sectors),
                    desc=f'Computing impact grids for `{city.name.upper()}` sectors'
                )
            ]
            print(f"Calculation sectors for `{city.name.upper()}` has taken: {time.time() - st} sec")

            st_hexagons = time.time()
            print(f"Start generating hexagons for `{city.name.upper()}`.")
            hexagons = generate_hexagons_by_impact_grid_cells(city, sectors, impact_grids, hexagons_edge_sizes)
            print(f"Generating hexagons for `{city.name.upper()}` has taken: {time.time() - st_hexagons} sec")

            st_save = time.time()
            save_hexagons(connection, hexagons)
            print(f"Saving hexagons to database for `{city.name.upper()}` has taken: {time.time() - st_save} sec")

            print(f"***** Total time for calculation `{city.name.upper()}`: {time.time() - st} sec")

    connection.close()
    print(f"------------------ TOTAL PIPELINE TIME: {time.time() - pipeline_start_time} SEC")
