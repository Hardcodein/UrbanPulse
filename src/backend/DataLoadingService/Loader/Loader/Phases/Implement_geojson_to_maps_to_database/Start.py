from pathlib import Path

# from Loader.Phases.Implement_geojson_to_maps_to_database import Fill_global_tables
import Fill_global_tables

def start_phase(database_url: str, data_path: str) -> None:
    Fill_global_tables.init_main_tables(database_url, data_path)


def main():
    dbstring = 'postgres://postgres:postgres_password@localhost:65432/maps_to_database'
    osm_dir = Path('D:\\UrbanPulse\\src\\backend\\DataLoadingService\\run_loader\\data')
    start_phase(dbstring,osm_dir)
 
if __name__ == "__main__":
 main()