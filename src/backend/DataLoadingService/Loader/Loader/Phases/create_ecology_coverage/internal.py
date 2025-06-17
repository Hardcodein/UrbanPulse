from dataclasses import dataclass
from typing import List

from shapely.geometry import LineString
from shapely.geometry import Polygon

from Loader.Loader.Entities.SetElement import SetElement


@dataclass
class Road:
    road_type: str
    line: LineString


@dataclass
class EcologyPOI:
    """Ecology Point Of Interest
    """
    impact: float
    polygon: Polygon


@dataclass
class ImpactParameters:
    settlements: List[SetElement]
    roads: List[Road]
    ecology_pois: List[EcologyPOI]
    forests: List[Polygon]
