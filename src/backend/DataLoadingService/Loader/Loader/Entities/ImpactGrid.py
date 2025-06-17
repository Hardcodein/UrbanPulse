from dataclasses import dataclass
from typing import Dict, List

from shapely import STRtree

from Loader.Loader.Entities.GridCell import GridCell


@dataclass
class ImpactGrid:
    cells: List[GridCell]
    str_tree_cells_inds: Dict[int, int]
    str_tree: STRtree