import argparse
import os
from pathlib import Path
import time
from typing import Dict, List

import psycopg2

from Loader.Models.Phase import Phase
from Loader.Services.DataProvider import DataProvider
from Loader.Services.FIlePhaseStatusStore import FilePhaseStatusStore
from Loader.Loader.Entities.HexagonSize import HexagonSize
from Loader.Loader.Phases.create_ecology_coverage import Start as create_ecology_coverage
from Loader.Loader.Phases.Implement_osm_to_maps_database import Start as implement_osm
from Loader.Phases.Human_density_coverage import Start as Human_density_coverage
from Loader.Phases.Preparation_tables import Start as Preparation_tables


def wait_for_db(db_url: str, retries: int = 30, delay: int = 2) -> None:
    """Ждёт готовности БД вместо слепого sleep."""
    print('Ожидание готовности БД...')
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            print('БД готова.')
            return
        except psycopg2.OperationalError:
            print(f'  Попытка {attempt}/{retries} — БД ещё не готова, жду {delay}с...')
            time.sleep(delay)
    raise RuntimeError('БД не стала доступна за отведённое время.')


def run_loader():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--osm-directory', required=True, default=Path('data'),
                        help='Рабочая директория с данными')
    parser.add_argument('--cities', required=True, default='all',
                        help='Список городов через запятую или "all"')
    parser.add_argument('--from-phase', required=False, default=None,
                        help='Начать с указанной фазы')
    parser.add_argument('--to-phase', required=False, default=None,
                        help='Закончить на указанной фазе')
    parser.add_argument('--continue', required=False, action='store_true',
                        default=argparse.SUPPRESS,
                        help='Продолжить с последней успешной фазы')

    arguments = parser.parse_args()

    osm_directory = Path(arguments.osm_directory)
    if osm_directory.is_file():
        raise AssertionError(f'{osm_directory} — файл, а не директория')
    osm_directory.mkdir(exist_ok=True, parents=True)

    cities = get_list_of_cities(arguments.cities)

    db_url = os.getenv('DATABASE_URL', 'postgres://postgres:postgres@host:5432/maps_to_database')
    psycopg2_proto = os.getenv('PSYCOPG2_PROTO', 'postgresql://')
    wait_for_db(psycopg2_proto + db_url)

    provider = _build_data_provider(osm_directory, cities)

    if hasattr(arguments, 'continue'):
        provider.execute_from_last_excellent_phase()
    else:
        provider.execute(arguments.from_phase, arguments.to_phase)


def _build_data_provider(osm_directory: Path, cities_list: List[str]) -> DataProvider:
    phase_status_folder = osm_directory / 'phase_statuses_file'
    phases = _build_phases(osm_directory, cities_list)
    store = FilePhaseStatusStore(phase_status_folder)
    return DataProvider(store, phases)


def _build_phases(osm_directory: Path, cities_list: List[str]) -> List[Phase]:
    db_url = os.getenv('DATABASE_URL', 'postgres://postgres:postgres@host:5432/maps_to_database')
    psycopg2_proto = os.getenv('PSYCOPG2_PROTO', 'postgresql://')
    db_conn_string = psycopg2_proto + db_url

    base_hexagon_edge_length_m = 100.
    hexagons_edge_sizes: Dict[HexagonSize, float] = {
        HexagonSize.base:   base_hexagon_edge_length_m,
        HexagonSize.s:      base_hexagon_edge_length_m * 2,
        HexagonSize.m:      base_hexagon_edge_length_m * 4,
        HexagonSize.l:      base_hexagon_edge_length_m * 8,
        HexagonSize.xl:     base_hexagon_edge_length_m * 10,
        HexagonSize.xxl:    base_hexagon_edge_length_m * 12,
        HexagonSize.xxxl:   base_hexagon_edge_length_m * 14,
        HexagonSize.xxxxl:  base_hexagon_edge_length_m * 16,
        HexagonSize.xxxxxl: base_hexagon_edge_length_m * 18,
    }

    resources_directory = os.getenv(
        'RESOURCES_DIR',
        str(Path(__file__).parent.parent / 'res' / 'fill_OpetStreetMap_to_maps_database')
    )

    return [
        Phase(
            serial_number=0,
            name='preparation_tables',
            description='Подготовка таблиц БД (гексагоны, аналитика)',
            execution_method=Preparation_tables.start_phase,
            execution_args=(db_conn_string,)
        ),
        Phase(
            serial_number=1,
            name='implement_osm',
            description='Импорт OSM данных через imposm3 (скачивает PBF если нет)',
            execution_method=implement_osm.start_phase,
            execution_args=(
                db_conn_string,
                resources_directory,
                str(osm_directory),
                cities_list,
            )
        ),
        Phase(
            serial_number=2,
            name='create_ecology_coverage',
            description='Расчёт экологического покрытия по гексагонам',
            execution_method=create_ecology_coverage.start_phase,
            execution_args=(
                db_conn_string,
                hexagons_edge_sizes,
                2000.,   # ecology_r_m
                200.,    # grid_cell_side_m
                10.,     # segment_length_m
                3000.,   # sector_size_m
                osm_directory,
                cities_list,
            )
        ),
        Phase(
            serial_number=3,
            name='create_human_density_coverage',
            description='Расчёт плотности населения по гексагонам',
            execution_method=Human_density_coverage.start_phase,
            execution_args=(db_conn_string,)
        ),
    ]


def get_list_of_cities(string: str) -> List[str]:
    cities = string.lower().strip().split(',')
    if len(cities) == 1 and cities[0] == 'all':
        return []
    return [c.strip() for c in cities if c.strip()]


if __name__ == '__main__':
    run_loader()
