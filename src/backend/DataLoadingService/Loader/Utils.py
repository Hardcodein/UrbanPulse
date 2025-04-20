
def get_list_of_cities(string):
    cities = string.lower().strip().split(',')
    if len(cities) == 1 and cities[0] == "all":
        return []