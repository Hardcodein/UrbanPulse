from pathlib import Path

import Loader.Loader.Phases.Change_osm_data_phase.Change_buildings_part as bld_parts
from Loader.Loader.Phases.Change_osm_data_phase.Change_water import change_water
from Loader.Loader.Phases.Change_osm_data_phase.Preparation_subways import preparation_subways


def start_phase(database_url: str, 
              osm_directory: Path):
    change_water(database_url)
    preparation_subways(database_url, osm_directory)
    bld_parts.fix_buildings(database_url)
