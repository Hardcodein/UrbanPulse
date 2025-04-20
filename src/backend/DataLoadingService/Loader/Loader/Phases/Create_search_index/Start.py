from Loader.Loader.Phases.Create_search_index.Create_search_index import main_create_index


def start_phase(database_url: str, destination_dir: str):
    main_create_index(database_url, destination_dir)