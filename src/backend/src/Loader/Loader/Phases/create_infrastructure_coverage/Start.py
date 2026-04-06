

from fill_infrastructure_tables import create_infrastructure_pois
import calc_density as bld_pct
import create_infrastructure_coverage as inf_cov

def start_phase(database_url: str, navigation_url: str):
    bld_pct.calc_density(database_url)
    #create_infrastructure_pois(database_url)
    #inf_cov.create_coverage(database_url, navigation_url)

def main():
    dbstring = 'postgresql://postgres:postgres_password@localhost:65432/maps_to_database'
    navigationstring = 'http://localhost:8002'
    start_phase(dbstring,navigationstring)
 
if __name__ == "__main__":
 main()