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
    private static readonly HashSet<string> ValidSources = ["analytics"];

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
