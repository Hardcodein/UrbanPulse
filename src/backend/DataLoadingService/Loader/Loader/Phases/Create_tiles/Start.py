from pathlib import Path

import Loader.Phases.Create_tiles.Create_tiles as Create_tiles


def start_phase(database_url_string: str, 
                osm_dir_directory: Path, 
                root_tiles_path: Path): 
    Create_tiles.main_create_tiles(database_url_string, osm_dir_directory, root_tiles_path, threads_count=4)
