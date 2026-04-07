
from dataclasses import dataclass
from shapely.geometry import Point,Polygon
from Loader.Loader.Entities.Bounds import Bounds


@dataclass
class GridCell:
    impact: float
    center: Point
    bounds: Bounds
    polygon: Polygon
