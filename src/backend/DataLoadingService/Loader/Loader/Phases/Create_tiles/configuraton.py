# -*- coding: utf-8 -*-

THREADS_COUNT = 2

# Directory for saving tiles:

default_source = "osm"

sources = [
    {
        "name": "global",
        # Bounding for tiles consisting of 2 points. Southwest and Northeast
        # World boundaries.
        # if you set abs(lat) to more then 85 degrees, you will have negative y.
        "bbox_p1_deg": [-85.0, -180.0],  # lat, lon
        "bbox_p2_deg": [85.0, 180.0],

        "def_min_zoom": 0,
        "def_max_zoom": 7,
        # 0, 1, 2, 3, 4, 5
        "zoom_levels": [0, 1, 2, 3, 4, 5, 6, 7]
    },
    {
        "name": "analytics",

        "def_min_zoom": 6,
        "def_max_zoom": 15,

        "zoom_levels": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    },
    {
        "name": default_source,

        "def_min_zoom": 6,
        "def_max_zoom": 15,

        "zoom_levels": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    }
]

implement_cities = "'Москва','Санкт-Петербург','Ростов-на-Дону', " \
                   "'Краснодар', 'Сочи',"

small_towns = "'Scientific station', 'Historic place', 'Meteorogical Station', 'Populated place'"

switch_for_building_type = "CASE WHEN type in ('industrial', 'garages', 'warehouse', 'service', " \
                           "'manufacture', 'hangar') THEN 'i' " \
                           "WHEN type in ('house', 'residential', 'apartments', 'detached', 'terrace', " \
                           "'semidetached_house', 'cabin', 'bungalow', 'semi', 'yes') THEN 'l' ELSE  'c' END as type"

# Layers of vector tiles:
layers = [
    {
        "layer_name": "ecology_poi",
        "table": "ecology_poi",
        "fields": "poi_type, title as name, "
                  "CASE WHEN title_en <> '' THEN title_en ELSE NULL END as name_en, "
                  "CASE WHEN title_ru <> '' THEN title_ru ELSE NULL END as name_ru, "
                  "operator, url, start_year, energy_source, poi_subtype, owner",
        "source": "analytics",
        "additional_where": "and poi_type <> 'substation'"
    },
    {
        "layer_name": "infrastructure_poi",
        "table": "infrastructure_poi",
        "fields": "poi_type",
        "source": "analytics",
        "min_zoom": 6,
        "max_zoom": 7,
        "additional_where": "and min_level <= 6"
    },
    {
        "layer_name": "infrastructure_poi",
        "table": "infrastructure_poi",
        "fields": "poi_type",
        "source": "analytics",
        "min_zoom": 8,
        "max_zoom": 9,
        "additional_where": "and min_level <= 8"
    },
    {
        "layer_name": "infrastructure_poi",
        "table": "infrastructure_poi",
        "fields": "poi_type",
        "source": "analytics",
        "min_zoom": 10,
        "max_zoom": 11,
        "additional_where": "and min_level <= 9"
    },
    {
        "layer_name": "infrastructure_poi",
        "table": "infrastructure_poi",
        "fields": "poi_type",
        "source": "analytics",
        "min_zoom": 12,
        "max_zoom": 12,
        "additional_where": "and min_level <= 11"
    },
    {
        "layer_name": "infrastructure_poi",
        "table": "infrastructure_poi",
        "fields": "poi_type",
        "source": "analytics",
        "min_zoom": 13,
        "max_zoom": 13,
        "additional_where": "and min_level <= 12"
    },
    {
        "layer_name": "infrastructure_poi",
        "table": "infrastructure_poi",
        "fields": "poi_type",
        "source": "analytics",
        "min_zoom": 14,
        "max_zoom": 14
    },
    {
        "layer_name": "infrastructure_poi",
        "table": "infrastructure_poi",
        "fields": "poi_type, title as name, CASE WHEN title_en <> '' THEN title_en ELSE NULL END as name_en, CASE WHEN title_ru <> '' THEN title_ru ELSE NULL END as name_ru",
        "source": "analytics",
        "min_zoom": 15
    },
    {
        "layer_name": "hex",
        "table": "hex_tiles_xl",
        "fields": "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, "
                  "infrastructure::numeric::integer as infrastructure, life_quality,"
                  "filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
        "min_zoom": 6,
        "max_zoom": 8,
        "source": "analytics"
    },
    {
        "layer_name": "hex",
        "table": "hex_tiles_l",
        "fields": "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, "
                  "infrastructure::numeric::integer as infrastructure, life_quality,"
                  "filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
        "min_zoom": 9,
        "max_zoom": 9,
        "source": "analytics"
    },
    {
        "layer_name": "hex",
        "table": "hex_tiles_m",
        "fields": "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, "
                  "infrastructure::numeric::integer as infrastructure, life_quality,"
                  "filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
        "min_zoom": 10,
        "max_zoom": 10,
        "source": "analytics"
    },
    {
        "layer_name": "hex",
        "table": "hex_tiles_s",
        "fields": "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, "
                  "infrastructure::numeric::integer as infrastructure, life_quality,"
                  "filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
        "min_zoom": 11,
        "max_zoom": 11,
        "source": "analytics"
    },
    {
        "layer_name": "hex",
        "table": "hex_tiles",
        "fields": "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, "
                  "infrastructure::numeric::integer as infrastructure, life_quality,"
                  "filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
        "min_zoom": 12,
        "source": "analytics"
    },
    {
        "layer_name": "world_water_poly",
        "table": "world_oceans",
        "fields": "",
        "mode_clip": False,
        "max_zoom": 5,
        "source": "global"
    },
    {
        "layer_name": "world_water_poly",
        "table": "world_oceans_detailed",
        "fields": "",
        "mode_clip": False,
        "min_zoom": 6,
        "max_zoom": 7,
        "source": "global"
    },
    {
        "layer_name": "world_countries_poly",
        "table": "world_countries",
        "fields": "",
        "mode_clip": False,
        "max_zoom": 5,
        "source": "global"
    },
    {
        "layer_name": "world_countries_names",
        "table": "world_countries",
        "fields": "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "mode_clip": False,
        "source": "global",
        "geometry_operator": "centroid",
        "additional_where": "and scalerank < ",
        "append_zoom_to_additional_where": True
    },
    {
        "layer_name": "target_cities",
        "table": "world_cities",
        "fields": "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "mode_clip": False,
        "max_zoom": 5,
        "source": "global",
        "additional_where": f"and name_ru in ({implement_cities})"
    },
    {
        "layer_name": "world_cities",
        "table": "world_cities",
        "fields": "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, CASE "
                  "WHEN type = 'Admin-0 capital' THEN 'bb' "
                  "WHEN type = 'Admin-1 capital' THEN 'b' "
                  "ELSE  'c' "
                  "END as city_type ",
        "mode_clip": False,
        "max_zoom": 5,
        "source": "global",
        "additional_where": f"and name_ru not in ({implement_cities}) and type not in ({small_towns}) and scalerank <= ",
        "append_zoom_to_additional_where": True
    },
    {
        "layer_name": "buildings_parts",
        "table": "osm_building_parts_poly",
        "fields": f"{switch_for_building_type}, "
                  f"get_height_m(\"building_levels\", \"building_height\") as h, "
                  f"pct_building::numeric::integer as s, pct_dens_building::numeric::integer as v,"
                  f" infrastructure::numeric::integer as infrastructure",
        "min_zoom": 13,
        "max_zoom": 15,
        "additional_where": "and is_drawable = 1"
    },
    {
        "layer_name": "buildings",
        "table": "osm_buildings_poly",
        "fields": f"id, {switch_for_building_type}, "
                  f"get_height_m(\"building_levels\", \"building_height\") as h, "
                  f"pct_building::numeric::integer as s, pct_dens_building::numeric::integer as v,"
                  f" infrastructure::numeric::integer as infrastructure",
        "min_zoom": 13,
        "max_zoom": 14,
        "additional_where": "and is_drawable is null"
    },
    {
        "layer_name": "buildings",
        "table": "osm_buildings_poly",
        "fields": f"id, {switch_for_building_type}, "
                  "get_height_m(\"building_levels\", \"building_height\") as h, housenumber as n,"
                  "pct_building::numeric::integer as s, pct_dens_building::numeric::integer as v,"
                  " infrastructure::numeric::integer as infrastructure",
        "min_zoom": 15,
        "max_zoom": 15,
        "additional_where": "and is_drawable is null"
    },
    # Road sizes are used in styles.json to render road width.
    # We match road type to its size.
    {
        "layer_name": "roads",
        "table": "osm_roads_gen0",
        "fields": "",
        "min_zoom": 6,
        "max_zoom": 7
    },
    {
        "layer_name": "roads",
        "table": "osm_roads_gen1",
        "fields": "CASE "
                  "WHEN type = 'primary' THEN 'm' "
                  "ELSE  'l' "
                  "END as type, "
                  "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, "
                  "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, "
                  "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 8,
        "max_zoom": 9
    },
    {
        "layer_name": "roads",
        "table": "osm_roads_gen2",
        "fields": "CASE "
                  "WHEN type in ('motorway', 'trunk') THEN 'l' "
                  "WHEN type = 'primary' THEN 'm' "
                  "ELSE  's' "
                  "END as type, "
                  "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, "
                  "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, "
                  "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 10,
        "max_zoom": 11
    },
    {
        "layer_name": "roads",
        "table": "osm_roads_gen3",
        "fields": "CASE "
                  "WHEN type in ('motorway', 'trunk') THEN 'xxl' "
                  "WHEN type = 'primary' THEN 'xl' "
                  "WHEN type = 'secondary' THEN 'l' "
                  "WHEN type = 'tertiary' THEN 'm' "
                  "ELSE  's' "
                  "END as type, "
                  "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, "
                  "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, "
                  "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 12,
        "max_zoom": 12
    },
    {
        "layer_name": "roads",
        "table": "osm_roads_gen4",
        "fields": "CASE "
                  "WHEN type in ('motorway', 'motorway_link', 'trunk', 'trunk_link') THEN 'xxl' "
                  "WHEN type in ('primary', 'primary_link') THEN 'xl' "
                  "WHEN type in ('secondary', 'secondary_link') THEN 'l' "
                  "WHEN type in ('tertiary', 'tertiary_link') THEN 'm' "
                  "ELSE  's' "
                  "END as type, "
                  "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, "
                  "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, "
                  "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 13,
        "max_zoom": 13
    },
    {
        "layer_name": "roads",
        "table": "osm_roads_way",
        "fields": "CASE "
                  "WHEN type in ('motorway', 'motorway_link', 'trunk', 'trunk_link') THEN 'xxl' "
                  "WHEN type in ('primary', 'primary_link') THEN 'xl' "
                  "WHEN type in ('secondary', 'secondary_link') THEN 'l' "
                  "WHEN type in ('tertiary', 'tertiary_link') THEN 'm' "
                  "WHEN type in ('service', 'track', 'unclassified') THEN 'xs' "
                  "ELSE  's' "
                  "END as type, name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru ",
        "min_zoom": 14
    },
    {
        "layer_name": "footways",
        "table": "osm_footways_way",
        "fields": "",
        "min_zoom": 12,
        "max_zoom": 13,
        "additional_where": "and type = 'pedestrian'"
    },
    {
        "layer_name": "footways",
        "table": "osm_footways_way",
        "fields": "",
        "min_zoom": 14
    },
    {
        "layer_name": "railways",
        "table": "osm_railways_gen0",
        "fields": "",
        "min_zoom": 6,
        "max_zoom": 9,
        "additional_where": "and type not in ('monorail', 'tram')"
    },
    {
        "layer_name": "railways",
        "table": "osm_railways_gen1",
        "fields": "",
        "min_zoom": 10,
        "max_zoom": 11,
        "additional_where": "and type not in ('monorail', 'tram')"
    },
    {
        "layer_name": "railways",
        "table": "osm_railways_gen2",
        "fields": "",
        "min_zoom": 12,
        "max_zoom": 12,
        "additional_where": "and type not in ('monorail', 'tram')"
    },
    {
        "layer_name": "railways",
        "table": "osm_railways_way",
        "fields": "",
        "min_zoom": 13,
        "additional_where": "and type not in ('monorail', 'tram')"
    },
    {
        "layer_name": "trams",
        "table": "osm_railways_gen2",
        "fields": "",
        "min_zoom": 12,
        "max_zoom": 12,
        "additional_where": "and type in ('monorail', 'tram')"
    },
    {
        "layer_name": "trams",
        "table": "osm_railways_way",
        "fields": "",
        "min_zoom": 13,
        "additional_where": "and type in ('monorail', 'tram')"
    },
    {
        "layer_name": "osm_subway_route_members",
        "table": "osm_subway_route_members",
        "fields": "colour",
        "additional_where": "and handled=1",
        "min_zoom": 9
    },
    {
        "layer_name": "residential",
        "table": "osm_residential_zones",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 14
    },
    {
        "layer_name": "natural",
        "table": "osm_natural_gen0",
        "fields": "",
        "min_zoom": 6,
        "max_zoom": 8
    },
    {
        "layer_name": "natural",
        "table": "osm_natural_gen1",
        "fields": "",
        "min_zoom": 9,
        "max_zoom": 10
    },
    {
        "layer_name": "natural",
        "table": "osm_natural_gen2",
        "fields": "",
        "min_zoom": 11,
        "max_zoom": 12
    },
    {
        "layer_name": "natural",
        "table": "osm_natural_gen3",
        "fields": "",
        "min_zoom": 13,
        "max_zoom": 13
    },
    {
        "layer_name": "natural",
        "table": "osm_natural_poly",
        "fields": "",
        "min_zoom": 14
    },
    {
        "layer_name": "natural_name",
        "table": "osm_natural_gen1",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 12,
        "max_zoom": 12
    },
    {
        "layer_name": "natural_water",
        "table": "osm_natural_water_gen0",
        "fields": "",
        "min_zoom": 6,
        "max_zoom": 8
    },
    {
        "layer_name": "natural_water",
        "table": "osm_natural_water_gen1",
        "fields": "",
        "min_zoom": 9,
        "max_zoom": 10
    },
    {
        "layer_name": "natural_water",
        "table": "osm_natural_water_gen2",
        "fields": "",
        "min_zoom": 11,
        "max_zoom": 12
    },
    {
        "layer_name": "natural_water",
        "table": "osm_natural_water_poly",
        "fields": "",
        "min_zoom": 13
    },
    {
        "layer_name": "waterways",
        "table": "osm_waterways_gen0",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 11,
        "max_zoom": 11
    },
    {
        "layer_name": "waterways",
        "table": "osm_waterways_gen1",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 12,
        "max_zoom": 12
    },
    {
        "layer_name": "waterways",
        "table": "osm_waterways_way",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 13
    },
    {
        "layer_name": "landuse_industrial",
        "table": "osm_industrial_zones_gen1",
        "fields": "",
        "min_zoom": 11,
        "max_zoom": 12
    },
    {
        "layer_name": "landuse_industrial",
        "table": "osm_industrial_zones",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 13
    },
    {
        "layer_name": "landuse_cemetery",
        "table": "osm_cemeteries_gen0",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 10,
        "max_zoom": 10
    },
    {
        "layer_name": "landuse_cemetery",
        "table": "osm_cemeteries_gen1",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 11,
        "max_zoom": 11
    },
    {
        "layer_name": "landuse_cemetery",
        "table": "osm_cemeteries_poly",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 12
    },
    {
        "layer_name": "landuse_grass",
        "table": "osm_landuse_grass_gen0",
        "fields": "",
        "min_zoom": 9,
        "max_zoom": 10
    },
    {
        "layer_name": "landuse_grass",
        "table": "osm_landuse_grass_gen1",
        "fields": "",
        "min_zoom": 11,
        "max_zoom": 12
    },
    {
        "layer_name": "landuse_grass",
        "table": "osm_landuse_grass_gen2",
        "fields": "",
        "min_zoom": 13,
        "max_zoom": 13
    },
    {
        "layer_name": "landuse_grass",
        "table": "osm_landuse_grass_poly",
        "fields": "",
        "min_zoom": 14
    },
    {
        "layer_name": "towns",
        "table": "osm_place_point",
        "fields": "CASE "
                  "WHEN capital THEN 'tgt' "
                  "WHEN type = 'city' THEN 'c' "
                  "ELSE  't' "
                  "END as t ",
        "min_zoom": 6,
        "max_zoom": 7,
        "additional_where": f"and type in ('city', 'town') and population > 60000"
    },
    {
        "layer_name": "towns",
        "table": "osm_place_point",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, CASE "
                  "WHEN capital THEN 'tgt' "
                  "WHEN type = 'city' THEN 'c' "
                  "ELSE  't' "
                  "END as t ",
        "min_zoom": 8,
        "max_zoom": 8,
        "additional_where": f"and type in ('city', 'town') and population > 20000"
    },
    {
        "layer_name": "towns",
        "table": "osm_place_point",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, CASE "
                  "WHEN capital THEN 'tgt' "
                  "WHEN type = 'city' THEN 'c' "
                  "ELSE  't' "
                  "END as t ",
        "min_zoom": 9,
        "max_zoom": 9,
        "additional_where": f"and type in ('city', 'town')"
    },
    {
        "layer_name": "towns",
        "table": "osm_place_point",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, CASE "
                  "WHEN capital THEN 'tgt' "
                  "WHEN type = 'city' THEN 'c' "
                  "WHEN type = 'town' THEN 't' "
                  "ELSE  'v' "
                  "END as t ",
        "min_zoom": 10,
        "max_zoom": 10
    },
    {
        "layer_name": "towns",
        "table": "osm_place_point",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, CASE "
                  "WHEN type = 'village' THEN 'v' "
                  "WHEN type = 'hamlet' THEN 'h' "
                  "ELSE  'd' "
                  "END as t ",
        "min_zoom": 11,
        "max_zoom": 11,
        "additional_where": f"and type not in ('city', 'town')"
    },
    {
        "layer_name": "admin_names",
        "table": "osm_admin_level_poly",
        "fields": "ref as name",
        "min_zoom": 7,
        "max_zoom": 9,
        "additional_where": "and admin_level = 5",
        "geometry_operator": "centroid"
    },
    {
        "layer_name": "admin_names",
        "table": "osm_admin_level_poly",
        "fields": "trim(both ' ' from replace(lower(name), 'район', '')) as name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
        "min_zoom": 10,
        "max_zoom": 11,
        "additional_where": "and admin_level = 8",
        "geometry_operator": "centroid"
    },
    {
        "layer_name": "admin_borders",
        "table": "osm_admin_level_poly",
        "fields": "geometry",
        "min_zoom": 6,
        "max_zoom": 9,
        "additional_where": "and admin_level >= 5 and admin_level < 9"
    },
    {
        "layer_name": "admin_borders",
        "table": "osm_admin_level_poly",
        "fields": "geometry",
        "min_zoom": 10,
        "max_zoom": 11,
        "additional_where": "and admin_level >= 5"
    },
    {
        "layer_name": "subway_stations",
        "table": "osm_subway_stations",
        "fields": "city",
        "min_zoom": 11,
        "max_zoom": 11,
        "additional_where": "and railway = 'station'",
    },
    {
        "layer_name": "subway_stations",
        "table": "osm_subway_stations",
        "fields": "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, city",
        "min_zoom": 12,
        "additional_where": "and railway = 'station'"
    },
    {
        "layer_name": "subway_entrances",
        "table": "osm_subway_station_entrances",
        "fields": "city",
        "min_zoom": 14
    }
]