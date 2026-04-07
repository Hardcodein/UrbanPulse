namespace TileService.Services;

public interface ITileService
{
    Task<byte[]?> GetTileAsync(string source, int z, int x, int y);
}
