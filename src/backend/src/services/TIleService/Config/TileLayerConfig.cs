namespace TileService.Config;

/// <summary>
/// Описание одного слоя векторного тайла.
/// Порт configuraton.py → layers[]
/// </summary>
public sealed record TileLayer(
    string Name,          // layer_name
    string Table,         // table
    string Fields,        // fields (SQL выражения)
    string Source,        // "osm" | "analytics" | "global"
    int MinZoom,
    int MaxZoom,
    string? Where = null, // additional_where
    bool AppendZoom = false,  // append_zoom_to_additional_where
    string? GeometryOperator = null // "centroid" | "line_merge" | null
);

/// <summary>
/// Реестр всех слоёв и источников.
/// Соответствует configuraton.py: sources + layers.
/// </summary>
public sealed class TileLayerConfig
{
    // Источники тайлов (аналог sources[] в configuraton.py)
    private static readonly HashSet<string> ValidSources = ["osm", "analytics", "global"];

    // Все слои — порт списка layers[] из configuraton.py
    private static readonly List<TileLayer> AllLayers =
    [
        // ── analytics source ──────────────────────────────────────────────
        new("ecology_poi", "ecology_poi",
            "poi_type, title as name, " +
            "CASE WHEN title_en <> '' THEN title_en ELSE NULL END as name_en, " +
            "CASE WHEN title_ru <> '' THEN title_ru ELSE NULL END as name_ru, " +
            "operator, url, start_year, energy_source, poi_subtype, owner",
            "analytics", 6, 15,
            Where: "and poi_type <> 'substation'"),

        new("infrastructure_poi", "infrastructure_poi", "poi_type",
            "analytics", 6, 7, Where: "and min_level <= 6"),
        new("infrastructure_poi", "infrastructure_poi", "poi_type",
            "analytics", 8, 9, Where: "and min_level <= 8"),
        new("infrastructure_poi", "infrastructure_poi", "poi_type",
            "analytics", 10, 11, Where: "and min_level <= 9"),
        new("infrastructure_poi", "infrastructure_poi", "poi_type",
            "analytics", 12, 12, Where: "and min_level <= 11"),
        new("infrastructure_poi", "infrastructure_poi", "poi_type",
            "analytics", 13, 13, Where: "and min_level <= 12"),
        new("infrastructure_poi", "infrastructure_poi", "poi_type",
            "analytics", 14, 14),
        new("infrastructure_poi", "infrastructure_poi",
            "poi_type, title as name, " +
            "CASE WHEN title_en <> '' THEN title_en ELSE NULL END as name_en, " +
            "CASE WHEN title_ru <> '' THEN title_ru ELSE NULL END as name_ru",
            "analytics", 15, 15),

        // Гексагоны аналитики — разные таблицы по зумам
        new("hex", "hex_tiles_xl",
            "bld_pct::numeric::integer as s",
            "analytics", 6, 8),
        new("hex", "hex_tiles_l",
            "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, " +
            "bld_human_density::numeric::integer as h, infrastructure::numeric::integer as infrastructure, " +
            "life_quality, filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
            "analytics", 9, 9),
        new("hex", "hex_tiles_m",
            "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, " +
            "bld_human_density::numeric::integer as h, infrastructure::numeric::integer as infrastructure, " +
            "life_quality, filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
            "analytics", 10, 10),
        new("hex", "hex_tiles_s",
            "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, " +
            "bld_human_density::numeric::integer as h, infrastructure::numeric::integer as infrastructure, " +
            "life_quality, filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
            "analytics", 11, 11),
        new("hex", "hex_tiles",
            "impact, bld_pct::numeric::integer as s, bld_dens_pct::numeric::integer as v, " +
            "bld_human_density::numeric::integer as h, infrastructure::numeric::integer as infrastructure, " +
            "life_quality, filter_subway, filter_park, filter_where_to_eat, filter_school, filter_kindergarten, filter_shop",
            "analytics", 12, 15),

        // ── global source ─────────────────────────────────────────────────
        new("world_water_poly", "world_oceans", "", "global", 0, 5),
        new("world_water_poly", "world_oceans_detailed", "", "global", 6, 7),
        new("world_countries_poly", "world_countries", "", "global", 0, 5),
        new("world_countries_names", "world_countries",
            "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "global", 0, 15,
            Where: "and scalerank < ", AppendZoom: true,
            GeometryOperator: "centroid"),
        new("target_cities", "world_cities",
            "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "global", 0, 5,
            Where: "and name_ru in ('Санкт-Петербург')"),
        new("world_cities", "world_cities",
            "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, " +
            "CASE WHEN type = 'Admin-0 capital' THEN 'bb' WHEN type = 'Admin-1 capital' THEN 'b' ELSE 'c' END as city_type",
            "global", 0, 5,
            Where: "and name_ru not in ('Санкт-Петербург') and type not in ('Scientific station','Historic place','Meteorogical Station','Populated place') and scalerank <= ",
            AppendZoom: true),

        // ── osm source ────────────────────────────────────────────────────
        new("buildings_parts", "osm_building_parts_poly",
            "CASE WHEN type in ('industrial','garages','warehouse','service','manufacture','hangar') THEN 'i' " +
            "WHEN type in ('house','residential','apartments','detached','terrace','semidetached_house','cabin','bungalow','semi','yes') THEN 'l' ELSE 'c' END as type, " +
            "get_height_m(\"building_levels\", \"building_height\") as h, " +
            "pct_building::numeric::integer as s, pct_dens_building::numeric::integer as v, " +
            "infrastructure::numeric::integer as infrastructure",
            "osm", 13, 15, Where: "and is_drawable = 1"),
        new("buildings", "osm_buildings_poly",
            "id, CASE WHEN type in ('industrial','garages','warehouse','service','manufacture','hangar') THEN 'i' " +
            "WHEN type in ('house','residential','apartments','detached','terrace','semidetached_house','cabin','bungalow','semi','yes') THEN 'l' ELSE 'c' END as type, " +
            "get_height_m(\"building_levels\", \"building_height\") as h, " +
            "pct_building::numeric::integer as s, pct_dens_building::numeric::integer as v, " +
            "infrastructure::numeric::integer as infrastructure",
            "osm", 13, 14, Where: "and is_drawable is null"),
        new("buildings", "osm_buildings_poly",
            "id, CASE WHEN type in ('industrial','garages','warehouse','service','manufacture','hangar') THEN 'i' " +
            "WHEN type in ('house','residential','apartments','detached','terrace','semidetached_house','cabin','bungalow','semi','yes') THEN 'l' ELSE 'c' END as type, " +
            "get_height_m(\"building_levels\", \"building_height\") as h, housenumber as n, " +
            "pct_building::numeric::integer as s, pct_dens_building::numeric::integer as v, " +
            "infrastructure::numeric::integer as infrastructure",
            "osm", 15, 15, Where: "and is_drawable is null"),

        new("roads", "osm_roads_gen0", "", "osm", 6, 7),
        new("roads", "osm_roads_gen1",
            "CASE WHEN type = 'primary' THEN 'm' ELSE 'l' END as type, " +
            "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, " +
            "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 8, 9),
        new("roads", "osm_roads_gen2",
            "CASE WHEN type in ('motorway','trunk') THEN 'l' WHEN type = 'primary' THEN 'm' ELSE 's' END as type, " +
            "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, " +
            "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 10, 11),
        new("roads", "osm_roads_gen3",
            "CASE WHEN type in ('motorway','trunk') THEN 'xxl' WHEN type = 'primary' THEN 'xl' " +
            "WHEN type = 'secondary' THEN 'l' WHEN type = 'tertiary' THEN 'm' ELSE 's' END as type, " +
            "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, " +
            "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 12, 12),
        new("roads", "osm_roads_gen4",
            "CASE WHEN type in ('motorway','motorway_link','trunk','trunk_link') THEN 'xxl' " +
            "WHEN type in ('primary','primary_link') THEN 'xl' WHEN type in ('secondary','secondary_link') THEN 'l' " +
            "WHEN type in ('tertiary','tertiary_link') THEN 'm' ELSE 's' END as type, " +
            "CASE WHEN short_name <> '' THEN short_name ELSE name END as name, " +
            "CASE WHEN short_name_en <> '' THEN short_name_en WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN short_name_ru <> '' THEN short_name_ru WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 13, 13),
        new("roads", "osm_roads_way",
            "CASE WHEN type in ('motorway','motorway_link','trunk','trunk_link') THEN 'xxl' " +
            "WHEN type in ('primary','primary_link') THEN 'xl' WHEN type in ('secondary','secondary_link') THEN 'l' " +
            "WHEN type in ('tertiary','tertiary_link') THEN 'm' WHEN type in ('service','track','unclassified') THEN 'xs' " +
            "ELSE 's' END as type, name, " +
            "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 14, 15),

        new("footways", "osm_footways_way", "", "osm", 12, 13, Where: "and type = 'pedestrian'"),
        new("footways", "osm_footways_way", "", "osm", 14, 15),

        new("railways", "osm_railways_gen0", "", "osm", 6, 9, Where: "and type not in ('monorail','tram')"),
        new("railways", "osm_railways_gen1", "", "osm", 10, 11, Where: "and type not in ('monorail','tram')"),
        new("railways", "osm_railways_gen2", "", "osm", 12, 12, Where: "and type not in ('monorail','tram')"),
        new("railways", "osm_railways_way", "", "osm", 13, 15, Where: "and type not in ('monorail','tram')"),
        new("trams", "osm_railways_gen2", "", "osm", 12, 12, Where: "and type in ('monorail','tram')"),
        new("trams", "osm_railways_way", "", "osm", 13, 15, Where: "and type in ('monorail','tram')"),

        new("osm_subway_route_members", "osm_subway_route_members", "colour",
            "osm", 9, 15, Where: "and handled=1"),

        new("residential", "osm_residential_zones",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 14, 15),

        new("natural", "osm_natural_gen0", "", "osm", 6, 8),
        new("natural", "osm_natural_gen1", "", "osm", 9, 10),
        new("natural", "osm_natural_gen2", "", "osm", 11, 12),
        new("natural", "osm_natural_gen3", "", "osm", 13, 13),
        new("natural", "osm_natural_poly", "", "osm", 14, 15),
        new("natural_name", "osm_natural_gen1",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 12, 12),

        new("natural_water", "osm_natural_water_gen0", "", "osm", 6, 8),
        new("natural_water", "osm_natural_water_gen1", "", "osm", 9, 10),
        new("natural_water", "osm_natural_water_gen2", "", "osm", 11, 12),
        new("natural_water", "osm_natural_water_poly", "", "osm", 13, 15),

        new("waterways", "osm_waterways_gen0",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 11, 11),
        new("waterways", "osm_waterways_gen1",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 12, 12),
        new("waterways", "osm_waterways_way",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 13, 15),

        new("landuse_industrial", "osm_industrial_zones_gen1", "", "osm", 11, 12),
        new("landuse_industrial", "osm_industrial_zones",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 13, 15),

        new("landuse_cemetery", "osm_cemeteries_gen0",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 10, 10),
        new("landuse_cemetery", "osm_cemeteries_gen1",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 11, 11),
        new("landuse_cemetery", "osm_cemeteries_poly",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 12, 15),

        new("landuse_grass", "osm_landuse_grass_gen0", "", "osm", 9, 10),
        new("landuse_grass", "osm_landuse_grass_gen1", "", "osm", 11, 12),
        new("landuse_grass", "osm_landuse_grass_gen2", "", "osm", 13, 13),
        new("landuse_grass", "osm_landuse_grass_poly", "", "osm", 14, 15),

        new("towns", "osm_place_point",
            "CASE WHEN capital THEN 'tgt' WHEN type = 'city' THEN 'c' ELSE 't' END as t",
            "osm", 6, 7, Where: "and type in ('city','town') and population > 60000"),
        new("towns", "osm_place_point",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, " +
            "CASE WHEN capital THEN 'tgt' WHEN type = 'city' THEN 'c' ELSE 't' END as t",
            "osm", 8, 8, Where: "and type in ('city','town') and population > 20000"),
        new("towns", "osm_place_point",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, " +
            "CASE WHEN capital THEN 'tgt' WHEN type = 'city' THEN 'c' ELSE 't' END as t",
            "osm", 9, 9, Where: "and type in ('city','town')"),
        new("towns", "osm_place_point",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, " +
            "CASE WHEN capital THEN 'tgt' WHEN type = 'city' THEN 'c' WHEN type = 'town' THEN 't' ELSE 'v' END as t",
            "osm", 10, 10),
        new("towns", "osm_place_point",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, " +
            "CASE WHEN type = 'village' THEN 'v' WHEN type = 'hamlet' THEN 'h' ELSE 'd' END as t",
            "osm", 11, 11, Where: "and type not in ('city','town')"),

        new("admin_names", "osm_admin_level_poly", "ref as name",
            "osm", 7, 9, Where: "and admin_level = 5", GeometryOperator: "centroid"),
        new("admin_names", "osm_admin_level_poly",
            "trim(both ' ' from replace(lower(name), 'район', '')) as name, " +
            "CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, " +
            "CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru",
            "osm", 10, 11, Where: "and admin_level = 8", GeometryOperator: "centroid"),
        new("admin_borders", "osm_admin_level_poly", "geometry",
            "osm", 6, 9, Where: "and admin_level >= 5 and admin_level < 9"),
        new("admin_borders", "osm_admin_level_poly", "geometry",
            "osm", 10, 11, Where: "and admin_level >= 5"),

        new("subway_stations", "osm_subway_stations", "city",
            "osm", 11, 11, Where: "and railway = 'station'"),
        new("subway_stations", "osm_subway_stations",
            "name, CASE WHEN name_en <> '' THEN name_en ELSE NULL END as name_en, CASE WHEN name_ru <> '' THEN name_ru ELSE NULL END as name_ru, city",
            "osm", 12, 15, Where: "and railway = 'station'"),
        new("subway_entrances", "osm_subway_station_entrances", "city",
            "osm", 14, 15),
    ];

    /// <summary>
    /// Возвращает слои подходящие для данного источника и зума.
    /// </summary>
    public IReadOnlyList<TileLayer> GetLayers(string source, int z)
    {
        if (!ValidSources.Contains(source))
            return [];

        return AllLayers
            .Where(l => l.Source == source && z >= l.MinZoom && z <= l.MaxZoom)
            .ToList();
    }
}
