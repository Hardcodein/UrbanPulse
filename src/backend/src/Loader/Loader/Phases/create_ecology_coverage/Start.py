from pathlib import Path
from typing import Dict
from typing import List


from Loader.Loader.Phases.create_ecology_coverage.pipeline import create_ecology_coverage
from Loader.Loader.Entities.HexagonSize import HexagonSize

def get_list_of_cities(string):
    cities = string.lower().strip().split(',')
    if len(cities) == 1 and cities[0] == "all":
        return []
    
def start_phase(
        database_url: str,
        hexagons_edge_sizes: Dict[HexagonSize, float],
        ecology_r_m: float,
        grid_cell_side_m: float,
        segment_length_m: float,
        sector_size_m: float,
        osm_dir: Path,
        cities: List[str]
) -> None:
    create_ecology_coverage(
        database_url,
        hexagons_edge_sizes,
        ecology_r_m,
        grid_cell_side_m,
        segment_length_m,
        sector_size_m,
        osm_dir,
        cities,
    )

def main():


    
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
    osm_directory = Path('D:/UrbanPulse/src/backend/DataLoadingService/run_loader/data')
    # create_ecology_coverage_stage = Phase(
    #     order_number=4,
    #     name='create_ecology_coverage',
    #     description='',
    #     execution_method=create_ecology_coverage.start_phase,
    #     execution_args=(
    #         db_conn_string,
    #         hexagons_edge_sizes,
    #         ecology_r_m,
    #         grid_cell_side_m,
    #         segment_length_m,
    #         sector_size_m,
    #         osm_directory,
    #         cities_list
    #     )
    # )
    dbstring = 'postgresql://postgres:postgres_password@localhost:65432/maps_to_database'
    cities_list = get_list_of_cities('all')
    
    start_phase(dbstring,
                hexagons_edge_sizes,
                ecology_r_m,
                grid_cell_side_m,
                segment_length_m,
                sector_size_m,
                osm_directory,
                cities_list
                )
 
if __name__ == "__main__":
 main()

