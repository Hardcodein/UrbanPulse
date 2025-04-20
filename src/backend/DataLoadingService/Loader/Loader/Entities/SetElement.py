from dataclasses import dataclass
from typing import Optional

from shapely import Polygon

@dataclass
class SetElement:
    polygon: Polygon
    city_type: str
    city_type_impact: float
    population: Optional[int]
    population_impact: Optional[float]