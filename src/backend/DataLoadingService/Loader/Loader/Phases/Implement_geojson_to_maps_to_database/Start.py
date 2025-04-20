from Loader.Loader.Phases.Implement_geojson_to_maps_to_database.Fill_global_tables import init_main_tables


def start_phase(database_url: str, data_path: str) -> None:
    init_main_tables(database_url, data_path)