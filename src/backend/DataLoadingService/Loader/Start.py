
import argparse
import os
from pathlib import Path
import time
from typing import Dict, List

import psycopg2
from Loader.Models.Phase  import Phase    
from Loader.Services.DataProvider import DataProvider
from Loader.Services.FIlePhaseStatusStore import FilePhaseStatusStore
from Loader.Phases.Implement_geojson_to_maps_to_database import Start as Implement_geojson_to_maps_to_database
from Loader.Phases.Implement_osm_to_maps_database import Start as Implement_osm_to_maps_database
from Loader.Phases.Preparation_tables import Start as Preparation_tables
from Loader.Phases.Change_osm_data_phase import Start as Change_osm_data_phase
from Loader.Phases.Human_density_coverage import Start as Human_density_coverage
from Loader.Phases.Create_tiles import Start as Create_tiles
from Loader.Phases.Change_tables_for_search_index import Start as Change_tables_for_search_index
from Loader.Phases.Create_search_index import Start as Create_search_index
from Loader.Loader.Entities.HexagonSize import HexagonSize
from Loader.Loader.Phases.create_ecology_coverage import  Start as create_ecology_coverage


def run_loader():

    argumentParser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argumentParser.add_argument('--osm-directory',
                                 required=True, 
                                 default=Path('data'),
                                 help='Directory for download files')

    argumentParser.add_argument('--cities', 
                                required=True, 
                                default="all",
                                help="Cities")

    argumentParser.add_argument('--from-phase', 
                                required=False, 
                                default=None,
                                help='From phase')

    argumentParser.add_argument('--to-phase', 
                                required=False, 
                                default=None,
                                help="To phase")

    argumentParser.add_argument('--continue', 
                                required=False, 
                                action='store_true', 
                                default=argparse.SUPPRESS,
                                help="Continue running loader from last successful finished phase")
    

    arguments = argumentParser.parse_args()

    osm_directory = Path(arguments.osm_directory)
    if osm_directory.is_file():
        raise AssertionError(f"{osm_directory} is file, not directory")
    
    osm_directory.mkdir(exist_ok=True, 
                        parents=True)

    root_tiles_path = osm_directory / 'tiles'
    root_tiles_path.mkdir(exist_ok=True, parents=True)

    cities = get_list_of_cities(arguments.cities)

    # Остановка для инициализации контейнера базы данных
    print('Ожидание БД 30 секунд')
    time.sleep(30)
    print('Конец БД')

    data_prodider = start_data_provider(osm_directory, 
                                              root_tiles_path, 
                                              cities)

    if hasattr(arguments, 'continue'):
        data_prodider.execute_from_last_excellent_phase()
    else:
        data_prodider.execute(arguments.from_phase, arguments.to_phase)

def start_data_provider(osm_directory: Path, 
                            tiles_root_path: Path, 
                            cities_list: List[str]) -> DataProvider:
        
        res_folder = Path("res")

        phase_status_folder = Path(os.path.join(osm_directory,"phase_statuses_file"))

        phases_list = get_all_phases(res_folder, osm_directory, tiles_root_path, cities_list)
        
        phase_status_store = FilePhaseStatusStore(phase_status_folder)
 
        data_provider = DataProvider(phase_status_store, phases_list)

        return data_provider

def get_all_phases(
        resources_folder: Path,
        osm_directory: Path,
        root_tiles_path: Path,
        cities_list: List[str]
) -> List[Phase]:

    db_url = os.getenv("DATABASE_URL", "postgres://postgres:postgres_password@host:5432/maps_to_database")
   

    imposm_proto_postgis = os.getenv("IMPOSM_PROTO", "postgis://")
    
    psycopg2_proto = os.getenv("PSYCOPG2_PROTO", "postgresql://")
    #navigation_url = os.getenv("NAVIGATION_URL", "http://localhost:8002/sources_to_targets")
   
    # Импорт данных OpenStreetMap  в PostgreSQL
    implement_osm_to_maps_database_phase = Phase(
        serial_number=0,
        name='implement_osm_to_maps_database',
        description='Импорт данных OpenStreetMap  в PostgreSQL',
        execution_method=Implement_osm_to_maps_database.start_phase,
        execution_args=(imposm_proto_postgis+db_url, str(resources_folder / 'fill_OpetStreetMap_to_maps_database'), osm_directory, cities_list)
    )

    db_conn_string = psycopg2_proto + db_url
  
                        
    preparation_tables_phase = Phase(
        serial_number=1,
        name='preparation_tables',
        description='Подготовка таблиц БД к работе с географическими данными',
        execution_method=Preparation_tables.start_phase,
        execution_args=(db_conn_string,)
    )

    implement_geojson_to_maps_database_phase = Phase(
        serial_number=2,
        name='implement_geojson_to_maps_to_database',
        description='Импорт данных из ГеоJson в БД',
        execution_method=Implement_geojson_to_maps_to_database.start_phase,
        execution_args=(db_conn_string, str(resources_folder / 'Implement_geojson_to_maps_to_database'))
    )

    change_osm_data_phase = Phase(
        serial_number=3,
        name='change_osm_data',
        description='Обработка  зданий в PostgreSQL/PostGIS базе данных',
        execution_method=Change_osm_data_phase.start_phase,
        execution_args=(db_conn_string, osm_directory)
    )
    base_hexagon_edge_length_m = 100.
    hexagons_edge_sizes: Dict[HexagonSize, float] = {
        HexagonSize.base: base_hexagon_edge_length_m,
        HexagonSize.s: base_hexagon_edge_length_m * 2,
        HexagonSize.m: base_hexagon_edge_length_m * 4,
        HexagonSize.l: base_hexagon_edge_length_m * 8,
        HexagonSize.xl: base_hexagon_edge_length_m * 10,
        HexagonSize.xxl: base_hexagon_edge_length_m * 12,
        HexagonSize.xxxl: base_hexagon_edge_length_m * 14,
        HexagonSize.xxxxl: base_hexagon_edge_length_m * 16,
        HexagonSize.xxxxxl: base_hexagon_edge_length_m * 18
    }
    ecology_r_m = 2000.
    grid_cell_side_m = 200.
    segment_length_m = 10.
    sector_size_m = 3000.
    create_ecology_coverage_stage = Phase(
        order_number=4,
        name='create_ecology_coverage',
        description='',
        execution_method=create_ecology_coverage.start_phase,
        execution_args=(
            db_conn_string,
            hexagons_edge_sizes,
            ecology_r_m,
            grid_cell_side_m,
            segment_length_m,
            sector_size_m,
            osm_directory,
            cities_list
        )
    )

    create_human_density_coverage_phase =Phase(
        serial_number=4,
        name='create_human_density_coverage_phase',
        description='Создание слоя плотности населения людей',
        execution_method=Human_density_coverage.start_phase,
        execution_args=(db_conn_string,)
    )

    # create_infrastructure_coverage_stage = Stage(
    #     order_number=5,
    #     name='create_infrastructure_coverage',
    #     description='',
    #     execution_method=create_infrastructure_coverage.run_stage,
    #     execution_args=(db_conn_string, navigation_url)
    # )

    # create_filters_coverage_phase = Phase(
    #     order_number=6,
    #     name='create_filters_coverage',
    #     description='Fills fields in hexagon tables which correspond to subway proximity and other params',
    #     execution_method=create_filters_coverage.run_stage,
    #     execution_args=(
    #         db_conn_string, 
    #         navigation_url,
    #         osm_directory,
    #         cities_list
    #     )
    # )

    # create_life_quality_coverage_stage = Stage(
    #     order_number=7,
    #     name='create_life_quality_coverage',
    #     description='Fills fields in hexagon tables which correspond to life_quality',
    #     execution_method=create_life_quality_coverage.run_stage,
    #     execution_args=(
    #         db_conn_string, 
    #         osm_directory,
    #         cities_list
    #     )
    # )

    seed_tiles_phase = Phase(
        serial_number=0,#5
        name='create_tiles',
        description='Создание тайлов',
        execution_method=Create_tiles.start_phase,
        execution_args=(db_conn_string, osm_directory, root_tiles_path)
    )

    create_tables_for_search_index_phase = Phase(
        serial_number=1,
        name='create_tables_for_search_index',
        description='перенос данных из таблицы osm_place_point в таблицу osm_place_poly',
        execution_method=Change_tables_for_search_index.start_phase,
        execution_args=(db_conn_string,)
    )

    create_search_index_phase = Phase(
        serial_number=1,
        name='create_search_index',
        description='Построение поискового индекса географических объектов ',
        execution_method=Create_search_index.start_phase,
        execution_args=(db_conn_string, osm_directory)
    )

    all_stages = [
        implement_osm_to_maps_database_phase,
        preparation_tables_phase,
        #implement_geojson_to_maps_database_phase,
        #change_osm_data_phase,
        #create_human_density_coverage_phase,
        #create_infrastructure_coverage_stage,
        #create_filters_coverage_phase,
        #create_life_quality_coverage_stage,
        #seed_tiles_phase,
        #create_tables_for_search_index_phase,
        #create_search_index_phase
    ]
    return all_stages

def get_list_of_cities(string):
    cities = string.lower().strip().split(',')
    if len(cities) == 1 and cities[0] == "all":
        return []
     

if __name__ == '__main__':
    run_loader()
