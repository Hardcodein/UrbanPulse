from Loader.Loader.Phases.Change_tables_for_search_index.Change_tables import change_tables_for_search_index


def start_phase(database_url_string: str):
    change_tables_for_search_index(database_url_string)