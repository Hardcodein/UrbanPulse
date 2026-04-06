from pathlib import Path

#from Loader.Phases.Create_tiles import Create_tiles

import Create_tiles as Create_tiles


def start_phase(database_url_string: str, 
                osm_dir_directory: Path, 
                root_tiles_path: Path): 
    Create_tiles.main_create_tiles(database_url_string, osm_dir_directory, root_tiles_path, threads_count=4)

def main():
    dbstring = 'postgres://postgres:postgres_password@localhost:65432/maps_to_database'
    osm_dir = Path('D:\\UrbanPulse\\src\\backend\\DataLoadingService\\run_loader\\data')
    root_tiles_path = Path('D:\\UrbanPulse\\src\\backend\\DataLoadingService\\run_loader\\data\\tiles')
    start_phase(dbstring,osm_dir,root_tiles_path)
 
if __name__ == "__main__":
 main()