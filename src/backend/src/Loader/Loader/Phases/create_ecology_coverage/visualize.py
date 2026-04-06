from typing import List

import fiona
import pyproj
from fiona.crs import from_epsg
from geojson import Feature
from geojson import FeatureCollection
from geojson import dump
from shapely.geometry import mapping
from shapely.ops import transform

from Loader.Entities.ImpactGrid import ImpactGrid
from Loader.Entities.Sector import Sector
from Loader.Services.Utils import to_degrees

from internal import ImpactParameters

def dump_impact_grid_to_shapefile(
        sectors: List[Sector],
        impact_grids: List[ImpactGrid],
        filepath: str = 'ecology_cells.shp'
) -> None:
    schema = {
        'geometry': 'Polygon',
        'properties': {
            'sector_id': 'int',
            'impact': 'float'

        }
    }

    with fiona.open(filepath, 'w', 'ESRI Shapefile', schema=schema, crs=from_epsg(3857)) as out:
        transformer = pyproj.Transformer.from_crs(pyproj.CRS(4326), pyproj.CRS(3857), always_xy=True)
        for i, (sector, grid) in enumerate(zip(sectors, impact_grids)):
            cells_polygons = [cell.polygon for cell in grid.cells]
            cells_polygons = to_degrees(sector.scale_factor, cells_polygons)
            cells_polygons = [transform(transformer.transform, cell) for cell in cells_polygons]
            for polygon, cell in zip(cells_polygons, grid.cells):
                out.write(
                    {
                        'geometry': mapping(polygon),
                        'properties': {
                            'sector_id': i,
                            'impact': round(cell.impact, 4),
                        }
                    }
                )


def dump_city_data_to_geojson(
        impact_parameters: List[ImpactParameters],
        sectors: List[Sector],
        impact_grids: List[ImpactGrid],
        city_scale_factor: float,
        filepath: str = 'ecology_cells.geojson'
) -> None:
    features = [
        *get_features_for_impact_parameters(impact_parameters, city_scale_factor),
        *get_features_for_impact_cells(sectors, impact_grids)
    ]

    crs = {
        "type": "name",
        "properties": {
            "name": "EPSG:3857"
        }
    }
    features = FeatureCollection(features, crs=crs)
    with open(filepath, 'w') as file:
        dump(features, file)


def get_features_for_impact_parameters(
        all_impact_parameters: List[ImpactParameters],
        city_scale_factor: float
) -> List[Feature]:
    transformer = pyproj.Transformer.from_crs(pyproj.CRS(4326), pyproj.CRS(3857), always_xy=True)
    features = []
    for i, impact_parameters in enumerate(all_impact_parameters):
        settlements_polygons = [s.polygon for s in impact_parameters.settlements]
        settlements_polygons_wgs84 = to_degrees(city_scale_factor, settlements_polygons)
        settlements_polygons_web_mercator = [transform(transformer.transform, poly) for poly in
                                             settlements_polygons_wgs84]
        for poly, settlement in zip(settlements_polygons_web_mercator, impact_parameters.settlements):
            features.append(
                Feature(
                    geometry=poly,
                    properties={
                        'type': 'settlement',
                        'city_type': settlement.city_type,
                        'city_type_impact': settlement.city_type_impact,
                        'population': settlement.population,
                        'population_impact': settlement.population_impact,
                        'sector_id': i,
                    }
                )
            )

        road_lines = [road.line for road in impact_parameters.roads]
        road_lines_wgs84 = to_degrees(city_scale_factor, road_lines)
        road_lines_web_mercator = [transform(transformer.transform, line) for line in road_lines_wgs84]
        for line in road_lines_web_mercator:
            features.append(
                Feature(
                    geometry=line,
                    properties={
                        'type': 'road',
                        'sector_id': i,
                    }
                )
            )

        ecology_pois_polygons = [ep.polygon for ep in impact_parameters.ecology_pois]
        ecology_pois_polygons_wgs84 = to_degrees(city_scale_factor, ecology_pois_polygons)
        ecology_pois_polygons_web_mercator = [transform(transformer.transform, poly)
                                              for poly in ecology_pois_polygons_wgs84]
        for poly, ecology_poi in zip(ecology_pois_polygons_web_mercator, impact_parameters.ecology_pois):
            features.append(
                Feature(
                    geometry=poly,
                    properties={
                        'type': 'ecology_poi',
                        'impact': round(ecology_poi.impact, 2),
                        'sector_id': i,
                    }
                )
            )

        forests_polygons = impact_parameters.forests
        forests_polygons_wgs84 = to_degrees(city_scale_factor, forests_polygons)
        forests_polygons_web_mercator = [transform(transformer.transform, poly) for poly in forests_polygons_wgs84]
        for poly in forests_polygons_web_mercator:
            features.append(
                Feature(
                    geometry=poly,
                    properties={
                        'type': 'forest',
                        'sector_id': i,
                    }
                )
            )

    return features


def get_features_for_impact_cells(
        sectors: List[Sector],
        impact_grids: List[ImpactGrid],
) -> List[Feature]:
    transformer = pyproj.Transformer.from_crs(pyproj.CRS(4326), pyproj.CRS(3857), always_xy=True)
    features = []
    for i, (sector, grid) in enumerate(zip(sectors, impact_grids)):
        cells_polygons = [cell.polygon for cell in grid.cells]
        cells_polygons = to_degrees(sector.scale_factor, cells_polygons)
        cells_polygons = [transform(transformer.transform, cell) for cell in cells_polygons]
        for polygon, cell in zip(cells_polygons, grid.cells):
            features.append(
                Feature(
                    geometry=polygon,
                    properties={
                        'type': 'cell',
                        'sector_id': i,
                        'impact': round(cell.impact, 4),
                    }
                )
            )

    return features
