import json

def coordinants_from_text(text):
    object = json.loads(text)
    if object["type"] in ['Point', 'LineString']:
        return object["coordinates"]

    return object["coordinates"][0]

def get_rail_width():
    return 1.5

def get_line_width_and_default_lanes(highway):
    if highway in ["motorway", "motorway_link", "trunk", "trunk_link"]:
        return 3.75, 4

    if highway in ["primary", "primary_link", "secondary", "secondary_link"]:
        return 3.5, 4

    if highway in ["tertiary", "tertiary_link", "street", "living_street"]:
        return 3.5, 3

    if highway in ["road"]:
        return 3.0, 2

    return 2.75, 2
