import math
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.ops import unary_union

from Loader.Loader.Entities.ImpactGrid import ImpactGrid
from Loader.Loader.Entities.GridCell import GridCell
from Loader.Loader.Entities.SetElement import SetElement
from Loader.Loader.Phases.create_ecology_coverage.internal import EcologyPOI, ImpactParameters



def get_impact_by_population(population: Optional[float] = None) -> float:
    if population is None:
        return 0.
    if population < 10000:
        return 0.01
    if population < 50000:
        return 0.05
    if population < 100000:
        return 0.1
    if population < 500000:
        return 0.2
    if population < 1000000:
        return 0.3
    if population < 5000000:
        return 0.4
    if population < 10000000:
        return 0.6
    if population < 150000000:
        return 1.0
    if population < 20000000:
        return 1.2
    return 2.0


def get_impact_by_city_type(city_type: str) -> float:
    city_type_to_impact: Dict[str, float] = {
        "city": 1.0,
        "town": 0.5,
        "village": 0.3,
        "hamlet": 0.2,
        "isolated_dwelling": 0.1
    }
    return city_type_to_impact.get(city_type, 0.05)


def get_impact_by_road_type(road_type: str) -> float:
    if road_type in ["motorway", "motorway_link", "trunk", "trunk_link"]:
        return 60.

    if road_type in ["primary", "primary_link"]:
        return 20.

    if road_type in ["secondary", "secondary_link"]:
        return 10.

    if road_type in ["tertiary", "tertiary_link"]:
        return 3.

    return 1.


def get_settlement_impact_factor_for_cell(cell: GridCell, settlements: List[SetElement]) -> float:
    if len(settlements) == 0:
        # default value from `get_impact_by_city_type()`-function
        # need to be a parameter
        return 0.05

    intersected_settlements = [
        settlement
        for settlement in settlements
        if settlement.polygon.intersects(cell.polygon)
    ]

    if intersected_settlements:
        impact_population = max([
            get_impact_by_population(settlement.population)
            for settlement in intersected_settlements
        ])
        if impact_population > 0.:
            return impact_population
        else:
            impact_place_type = max([
                get_impact_by_city_type(settlement.city_type)
                for settlement in intersected_settlements
            ])
            return impact_place_type
    else:
        distances = [cell.center.distance(settlement.polygon) for settlement in settlements]
        closest_settlement = settlements[np.argmin(distances)]
        impact_population = get_impact_by_population(closest_settlement.population)
        if impact_population > 0.:
            return impact_population
        return get_impact_by_city_type(closest_settlement.city_type)


def get_equation_params(road_type: str, ecology_r_m: float) -> Tuple[float, float]:
    max_impact = get_impact_by_road_type(road_type)
    max_distance = ecology_r_m

    a = max_impact * max_impact / max_distance
    b = max_impact
    return a, b


def split_line_to_points(line: LineString, segment_length_m: float) -> List[Tuple[float, float]]:
    n_points = math.ceil(line.length / segment_length_m)
    points = [line.interpolate(i * segment_length_m) for i in range(n_points)]
    points = [(p.x, p.y) for p in points]
    return points


def compute_forest_coverage_ratios(
        grid: ImpactGrid,
        forests: List[Polygon]
) -> List[float]:
    cells_polygons = [cell.polygon for cell in grid.cells]
    cell, *_ = cells_polygons
    cell_square_m2 = cell.area
    forest_polygon = unary_union(forests)
    ratios = [0.] * len(grid.cells)
    try:
        intersection_indices = grid.str_tree.query(forest_polygon)
        intersection_indices = [
            idx for idx in intersection_indices 
            if 0 <= idx < len(grid.cells)  # Проверка валидности индекса
        ]
    except:
        return ratios
    for index in intersection_indices:
        ratio = grid.cells[index].polygon.intersection(forest_polygon).area / cell_square_m2
        ratios[index] = min(ratio, 1.0)

    return ratios


def compute_ecology_pois_impacts(
        grid: ImpactGrid,
        ecology_pois: List[EcologyPOI],
        ecology_r_m: float
) -> List[float]:
    impacts = []
    for cell in grid.cells:
        cell_impact = 0.
        for poi in ecology_pois:
            distance = cell.center.distance(poi.polygon)
            if distance > ecology_r_m:
                continue
            # y = - (a*x)^0.5 + b
            a = poi.impact * poi.impact / ecology_r_m
            b = poi.impact
            y = max(- math.sqrt(a * distance) + b, 0.)

            cell_impact += y
        impacts.append(cell_impact)

    return impacts


def compute_impact_value_in_grid_cells(
        grid: ImpactGrid,
        impact_parameters: ImpactParameters,
        ecology_r_m: float,
        segment_length_m: float = 10.
) -> None:
    road_points = []
    road_equation_params = []
    settlement_road_factor_mask = []
    for road in impact_parameters.roads:
        points = split_line_to_points(road.line, segment_length_m)
        equation_params = [get_equation_params(road.road_type, ecology_r_m)] * len(points)
        if road.road_type in ["unclassified", "street", "street_limited", "residential", "living_street", "road"]:
            settlement_mask = [True] * len(points)
        else:
            settlement_mask = [False] * len(points)

        road_points.extend(points)
        road_equation_params.extend(equation_params)
        settlement_road_factor_mask.extend(settlement_mask)

    road_points = np.array(road_points)
    road_equation_params = np.array(road_equation_params)
    settlement_road_factor_mask = np.array(settlement_road_factor_mask, dtype=bool)

    # road impact for cells
    road_impact_for_cells = []
    for cell in grid.cells:
        if road_points.size == 0:
            road_impact_for_cells.append(0.)
            continue
        settlement_impact_factor = get_settlement_impact_factor_for_cell(cell, impact_parameters.settlements)
        cell_center = np.array([cell.center.x, cell.center.y])
        distances = np.linalg.norm(road_points - cell_center, axis=1)
        too_far_mask = distances > ecology_r_m
        distances[too_far_mask] = 0.
        distances[settlement_road_factor_mask] *= settlement_impact_factor
        # y = - (a*x)^0.5 + b
        impacts = -np.sqrt(road_equation_params[:, 0] * distances) + road_equation_params[:, 1]
        impacts[impacts < 0.] = 0.
        # only road points which are inside ecology radius
        total_impact = np.sum(impacts[~too_far_mask])
        road_impact_for_cells.append(total_impact)

    ecology_poi_impact_for_cells = compute_ecology_pois_impacts(grid, impact_parameters.ecology_pois, ecology_r_m)

    # forest coverage ratio
    forest_coverage_ratios = compute_forest_coverage_ratios(grid, impact_parameters.forests)

    # final computing impacts
    for i, cell in enumerate(grid.cells):
        road_impact = road_impact_for_cells[i]
        ecology_impact = ecology_poi_impact_for_cells[i]
        total_impact = road_impact + ecology_impact
        forest_coverage_ratio = forest_coverage_ratios[i]

        cell.impact = (1 - forest_coverage_ratio) * total_impact + forest_coverage_ratio * (total_impact / 2.0)
