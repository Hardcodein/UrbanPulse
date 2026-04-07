from dataclasses import dataclass

from shapely.geometry import Polygon 

@dataclass
class City:
    id: int
    name: str
    scale_factor: float
    polygon: Polygon
    polygon_wgs84: Polygon
