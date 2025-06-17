#from Loader.Phases.Human_density_coverage.Calculation_human_density import calculation_human_density
from Calculation_human_density import calculation_human_density 

def start_phase(database_url_string: str)-> None:
    calculation_human_density(database_url_string)

def main():
    dbstring = 'postgresql://postgres:postgres_password@localhost:65432/maps_to_database'
    start_phase(dbstring)
 
if __name__ == "__main__":
 main()