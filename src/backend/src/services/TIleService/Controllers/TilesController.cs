using Microsoft.AspNetCore.Mvc;
using TileService.Services;

namespace TileService.Controllers;

[ApiController]
[Route("tiles")]
public sealed class TilesController : ControllerBase
{
    private readonly ITileService _tiles;

    public TilesController(ITileService tiles) => _tiles = tiles;

    /// <summary>
    /// Возвращает векторный тайл в формате Mapbox Vector Tiles (.pbf).
    /// Mapbox GL запрашивает: GET /tiles/{source}/{z}/{x}/{y}.pbf
    /// </summary>
    [HttpGet("{source}/{z:int}/{x:int}/{y:int}.pbf")]
    public async Task<IActionResult> GetTile(string source, int z, int x, int y)
    {
        if (z < 0 || z > 20 || x < 0 || y < 0)
            return BadRequest("Некорректные параметры тайла");

        var tile = await _tiles.GetTileAsync(source, z, x, y);

        // 204 No Content — стандартный ответ для пустых тайлов, Mapbox его понимает
        if (tile is null || tile.Length == 0)
            return NoContent();

        Response.Headers.Append("Cache-Control", "public, max-age=3600");
        Response.Headers.Append("Access-Control-Allow-Origin", "*");

        return File(tile, "application/x-protobuf");
    }

    /// <summary>
    /// Сброс кэша тайлов для источника (вызывается после обновления данных пайплайном).
    /// POST /tiles/{source}/cache/invalidate
    /// </summary>
    [HttpPost("{source}/cache/invalidate")]
    public IActionResult InvalidateCache(
        string source,
        [FromServices] Caching.TileCache cache)
    {
        cache.Invalidate(source);
        return Ok(new { message = $"Кэш источника '{source}' сброшен" });
    }
}
