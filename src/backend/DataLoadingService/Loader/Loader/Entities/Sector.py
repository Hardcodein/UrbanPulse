
from dataclasses import dataclass
from shapely.geometry import Point,Polygon
from Loader.Loader.Entities.Bounds import Bounds


@dataclass
class Sector:
    scale_factor: float
    polygon: Polygon
    polygon_wgs84: Polygon
    ecology_polygon_wgs84: Polygon
