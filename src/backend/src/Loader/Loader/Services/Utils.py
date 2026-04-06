import math
import json
import time
from functools import wraps
from typing import List
from typing import Tuple
from typing import Optional
from pathlib import Path
import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from shapely.ops import transform


from Loader.Loader.Entities.City import City
from Loader.Loader.Entities.Sector import Sector
from Loader.Loader.Entities.ImpactGrid import ImpactGrid
from Loader.Loader.Entities.GridCell import GridCell
from Loader.Loader.Entities.Bounds import Bounds


EARTH_R_M = 6371138  # average Earth radius in meters
EARTH_METRICS_DIAGONAL_SR = EARTH_R_M * np.pi / 180.  # SQRT(Earth sphere metrics diagonal)


def apply_for_args_and_kwargs(func: object) -> object:
    """
    Recursively apply func to all args and kwargs. Returns transformed (by func) arguments just as they were passed
    i.e. in the "*args, **kwargs" form.
    """

    @wraps(func)
    def do(*args, **kwargs):
        if len(kwargs) == 0:
            if len(args) > 1:
                return do(args)
            else:
                arg = args[0]
                if isinstance(arg, dict):
                    return {key: do(val) for key, val in arg.items()}
                elif isinstance(arg, (list, tuple, set)):
                    return arg.__class__(do(geom) for geom in arg)
                else:
                    return func(arg)
        else:
            return do(*args, kwargs)

    return do


def _transform_coordinates(*args, scale_factor: float, to: str, **kwargs):
    if not -1.0 <= scale_factor <= 1.0:
        raise ValueError('Cosine value must be in [-1.0; 1.0]')

    # Define scale functions, acting on shapely geometries:
    def scale_fun(geom):
        """
        Transform object's coordinates to metres or degrees

        :param geom: Shapely geometry object
        :return: Shapely geometry object with transformed coordinates
        """

        if to == 'm':
            return affinity.scale(
                geom,
                xfact=scale_factor * EARTH_METRICS_DIAGONAL_SR,
                yfact=EARTH_METRICS_DIAGONAL_SR,
                origin=(0, 0)
            )
        elif to == 'd':
            return affinity.scale(
                geom,
                xfact=1 / (scale_factor * EARTH_METRICS_DIAGONAL_SR),
                yfact=1 / EARTH_METRICS_DIAGONAL_SR,
                origin=(0, 0)
            )
        else:
            raise ValueError('`to` argument must be equal "m" or "d".')

    @apply_for_args_and_kwargs
    def do(obj):
        if issubclass(obj.__class__, (shapely.geometry.base.BaseGeometry, shapely.geometry.base.BaseMultipartGeometry)):
            return scale_fun(obj)
        elif obj is None:
            return None
        else:
            raise TypeError("Transformation doesn't support object type.")

    return do(*args, **kwargs)


def get_scale_factor(*args, **kwargs) -> float:
    bounds = []

    @apply_for_args_and_kwargs
    def get_bounds(obj):
        if issubclass(obj.__class__, (shapely.geometry.base.BaseGeometry, shapely.geometry.base.BaseMultipartGeometry)):
            bounds.append(obj.bounds)
        else:
            raise TypeError('Objects must be shapely geometry objects')

    get_bounds(*args, **kwargs)
    bounds = np.array(bounds).reshape(-1, 2)

    if np.any(np.max(bounds, axis=0) > (180, 90)) or np.any(np.min(bounds, axis=0) < (-180, -90)):
        raise ValueError("Incorrect bounds values. Object's bounds must be in EPSG:4326")

    return np.cos(np.mean(bounds, axis=0)[1] * np.pi / 180.)


def to_meters(*args, scale_factor: Optional[float] = None, **kwargs):
    scale_factor = scale_factor or get_scale_factor(*args, **kwargs)
    return scale_factor, _transform_coordinates(*args, scale_factor=scale_factor, to='m', **kwargs)


def to_degrees(scale_factor, *args, **kwargs):
    return _transform_coordinates(*args, scale_factor=scale_factor, to='d', **kwargs)


def get_hexagons(centers: List[Point], edge_length: float) -> List[Polygon]:
    angles = np.radians(60 * np.arange(6))
    deltas_x = np.cos(angles) * edge_length
    deltas_y = np.sin(angles) * edge_length

    centers = np.array([(p.x, p.y) for p in centers])
    centers_xs, centers_ys = centers[:, 0], centers[:, 1]
    xs = np.repeat(centers_xs, 6).reshape(-1, 6) + deltas_x
    ys = np.repeat(centers_ys, 6).reshape(-1, 6) + deltas_y
    hexagons_coords = np.column_stack((xs, ys)).reshape(-1, 1, 2, 6)

    polygons = [Polygon(coords[0].T) for coords in hexagons_coords]
    return polygons


def get_centers_of_hexagons_inside_bounds(
        left: float,
        bottom: float,
        right: float,
        top: float,
        edge_length: float
) -> List[Point]:
    # from here https://gis.stackexchange.com/q/341218
    grid = []

    v_step = math.sqrt(3) * edge_length
    h_step = 1.5 * edge_length

    h_skip = math.ceil(left / h_step) - 1
    h_start = h_skip * h_step

    v_skip = math.ceil(bottom / v_step) - 1
    v_start = v_skip * v_step

    h_end = right + h_step
    v_end = top + v_step

    if v_start - (v_step / 2.0) < bottom:
        v_start_array = [v_start + (v_step / 2.0), v_start]
    else:
        v_start_array = [v_start - (v_step / 2.0), v_start]

    v_start_idx = int(abs(h_skip) % 2)

    c_x = h_start
    c_y = v_start_array[v_start_idx]
    v_start_idx = (v_start_idx + 1) % 2
    while c_x < h_end:
        while c_y < v_end:
            grid.append(Point(c_x, c_y))
            c_y += v_step
        c_x += h_step
        c_y = v_start_array[v_start_idx]
        v_start_idx = (v_start_idx + 1) % 2

    return grid

def get_available_cities(osm_dir: Path, cities: List[str]) -> List[City]:
    # Later we should have a database which contains cities boundaries
    with open(str(osm_dir / "implement_cities.json"), "r", encoding="utf-8") as json_file:
        supported_cities = json.load(json_file)
    print(f"Parsed {len(supported_cities['cities'])} cities.")

    available_cities: List[City] = []
    for i, city in enumerate(supported_cities["cities"]):
        city_title = city["title_en"]

        if len(cities) > 0 and city_title not in cities:
            print("Skipping", city_title)
            continue

        with open(str(osm_dir / f"{city_title}_borders_for_clipping.geojson"), "r", encoding="utf-8") as borders_file:
            exterior, *interiors = json.loads(borders_file.read())['coordinates']

        polygon_wgs84 = Polygon(exterior, *interiors)
        scale_factor, polygon = to_meters(polygon_wgs84)
        available_cities.append(
            City(
                id=i,
                name=city_title,
                polygon=polygon,
                polygon_wgs84=polygon_wgs84,
                scale_factor=scale_factor
            )
        )
        print(f"Available city: {city_title}")

    return available_cities


def get_cell_centers(polygon: Polygon, cell_side_m: float) -> List[Tuple[float, float]]:
    left, bottom, right, top = polygon.bounds
    half_cell_m = cell_side_m / 2.

    n_cells_x = math.ceil((right - left) / cell_side_m)
    n_cells_y = math.ceil((top - bottom) / cell_side_m)
    start_x = left + ((right - left) - n_cells_x * cell_side_m) / 2. + half_cell_m
    start_y = bottom + ((top - bottom) - n_cells_y * cell_side_m) / 2. + half_cell_m
    cell_centers_xs = [
        start_x + cell_side_m * i
        for i in range(n_cells_x)
    ]
    cell_centers_ys = [
        start_y + cell_side_m * i
        for i in range(n_cells_y)
    ]
    cell_centers = []
    for x in cell_centers_xs:
        for y in cell_centers_ys:
            cell_centers.append((x, y))

    return cell_centers

def get_impact_grid_bounds(
        sector: Sector,
        grid_cell_side_m: float
) -> ImpactGrid:
    cell_centers = get_cell_centers(sector.polygon, grid_cell_side_m)

    half_cell_m = grid_cell_side_m / 2.
    grid_cells = []
    for (x, y) in cell_centers:
        left, bottom, right, top = x - half_cell_m, y - half_cell_m, x + half_cell_m, y + half_cell_m
        grid_cells.append(
            GridCell(
                impact=0.,
                center=Point(x, y),
                bounds=Bounds(left, bottom, right, top),
                polygon=Polygon.from_bounds(left, bottom, right, top)
            )
        )

    grid_cells = [cell for cell in grid_cells if sector.polygon.intersects(cell.polygon)]
    str_tree_cells_inds = {
        id(cell.polygon): i
        for i, cell in enumerate(grid_cells)
    }
    str_tree = STRtree([cell.polygon for cell in grid_cells])

    return ImpactGrid(
        cells=grid_cells,
        str_tree_cells_inds=str_tree_cells_inds,
        str_tree=str_tree
    )

def tranfrorm_grid_cells_to_web_mercator(transformer, sectors, impact_grids):
    st = time.time()
    print("Started transforming impact grid cells to Web Mercator")
    sectors_mercator = [transform(transformer.transform, sector.polygon_wgs84) for sector in sectors]
    sectors_str_tree_inds = {
        id(cell): i
        for i, cell in enumerate(sectors_mercator)
    }
    sectors_str_tree = STRtree(sectors_mercator)

    mercator_grids = []
    for sector, grid in zip(sectors, impact_grids):
        cells_polygons = [cell.polygon for cell in grid.cells]
        cells_polygons = to_degrees(sector.scale_factor, cells_polygons)
        cells_polygons = [transform(transformer.transform, cell) for cell in cells_polygons]
        cells = [
            GridCell(
                impact=cell.impact,
                center=None,
                bounds=None,
                polygon=polygon
            )
            for cell, polygon in zip(grid.cells, cells_polygons)
        ]
        str_tree_cells_inds = {
            id(cell.polygon): i
            for i, cell in enumerate(cells)
        }
        str_tree = STRtree(cells_polygons)
        mercator_grids.append(ImpactGrid(
            cells=cells,
            str_tree_cells_inds=str_tree_cells_inds,
            str_tree=str_tree
        ))
    print(f"Finished transforming impact grid cells to Web Mercator: {time.time() - st} sec")
    return mercator_grids, sectors_str_tree_inds, sectors_str_tree