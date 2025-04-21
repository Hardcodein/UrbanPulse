from Loader.Phases.Preparation_tables.Init_tables import create_tables


def start_phase(database_url_string: str) -> None:
    create_tables(database_url_string)