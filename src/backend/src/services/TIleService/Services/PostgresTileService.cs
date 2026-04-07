using System.Text;
using Dapper;
using Npgsql;
using TileService.Caching;
using TileService.Config;

namespace TileService.Services;

/// <summary>
/// Генерирует векторные тайлы (.pbf) на лету из PostGIS через ST_AsMVT.
/// Порт логики из Create_tiles.py → get_query() + generate_tile().
/// </summary>
public sealed class PostgresTileService : ITileService
{
    private readonly NpgsqlDataSource _dataSource;
    private readonly TileCache _cache;
    private readonly TileLayerConfig _config;
    private readonly ILogger<PostgresTileService> _logger;

    public PostgresTileService(
        NpgsqlDataSource dataSource,
        TileCache cache,
        TileLayerConfig config,
        ILogger<PostgresTileService> logger)
    {
        _dataSource = dataSource;
        _cache = cache;
        _config = config;
        _logger = logger;
    }

    public async Task<byte[]?> GetTileAsync(string source, int z, int x, int y)
    {
        // Проверяем кэш
        var cached = _cache.Get(source, z, x, y);
        if (cached is not null)
            return cached;

        var layers = _config.GetLayers(source, z);
        if (layers.Count == 0)
            return null;

        var sql = BuildMvtSql(layers, z, x, y);

        try
        {
            await using var conn = await _dataSource.OpenConnectionAsync();
            var tile = await conn.ExecuteScalarAsync<byte[]>(sql);

            if (tile is not null)
                _cache.Set(source, z, x, y, tile);

            return tile;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Ошибка генерации тайла {Source}/{Z}/{X}/{Y}", source, z, x, y);
            return null;
        }
    }

    /// <summary>
    /// Собирает SQL запрос с ST_AsMVT для всех слоёв тайла.
    /// Аналог get_query() + generate_tile() из Create_tiles.py.
    /// </summary>
    private static string BuildMvtSql(IReadOnlyList<TileLayer> layers, int z, int x, int y)
    {
        var sb = new StringBuilder("SELECT ");
        var seenNames = new HashSet<string>();
        var first = true;

        foreach (var layer in layers)
        {
            // Один layer_name может встречаться несколько раз в конфиге (разные таблицы по зумам)
            // но в одном тайле имя должно быть уникально — берём первое совпадение
            if (!seenNames.Add(layer.Name))
                continue;

            var (geomSelect, geomWhere) = GetGeometryExpressions(layer.GeometryOperator);

            var fields = string.IsNullOrEmpty(layer.Fields)
                ? ""
                : layer.Fields + ",";

            var where = BuildWhere(layer, z);

            var layerSql = $"""
                (SELECT ST_AsMVT(q_{layer.Name}, '{layer.Name}', 4096, 'geom')
                 FROM (
                   SELECT {fields} ST_AsMvtGeom({geomSelect}, BBox({x},{y},{z}), 4096, 64, true) AS geom
                   FROM {layer.Table}
                   WHERE ST_Intersects({geomWhere}, BBox({x},{y},{z})) {where}
                 ) AS q_{layer.Name})
                """;

            if (!first) sb.Append(" || ");
            sb.Append(layerSql);
            first = false;
        }

        return sb.ToString();
    }

    /// <summary>
    /// Возвращает SQL-выражения для geometry в SELECT и WHERE.
    /// Порт get_geometry() из Create_tiles.py.
    /// </summary>
    private static (string Select, string Where) GetGeometryExpressions(string? op) => op switch
    {
        "line_merge" => ("ST_LineMerge(ST_Collect(geometry))", "geometry"),
        "centroid"   => ("ST_Centroid(geometry)", "ST_Centroid(geometry)"),
        _            => ("geometry", "geometry"),
    };

    private static string BuildWhere(TileLayer layer, int z)
    {
        if (string.IsNullOrEmpty(layer.Where))
            return "";

        return layer.AppendZoom ? layer.Where + z : layer.Where;
    }
}
