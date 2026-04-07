from dataclasses import dataclass
from shapely import Polygon

from Loader.Loader.Entities.HexagonSize import HexagonSize


@dataclass
class EcologyHexagon:
    id: int
    impact: float
    polygon_web_mercator: Polygon
    hexagon_size: HexagonSize