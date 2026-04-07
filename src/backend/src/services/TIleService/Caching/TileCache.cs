using Microsoft.Extensions.Caching.Memory;

namespace TileService.Caching;

/// <summary>
/// Кэш тайлов в памяти процесса.
/// Тайлы меняются только после перезапуска пайплайна — кэшируем на 1 час.
/// Для production можно заменить на Redis (IDistributedCache).
/// </summary>
public sealed class TileCache
{
    private readonly IMemoryCache _cache;

    // Размер одной записи в условных единицах для ограничения памяти
    private static readonly MemoryCacheEntryOptions EntryOptions = new MemoryCacheEntryOptions()
        .SetAbsoluteExpiration(TimeSpan.FromHours(1))
        .SetSize(1);

    public TileCache(IMemoryCache cache) => _cache = cache;

    public byte[]? Get(string source, int z, int x, int y) =>
        _cache.TryGetValue(Key(source, z, x, y), out byte[]? tile) ? tile : null;

    public void Set(string source, int z, int x, int y, byte[] tile) =>
        _cache.Set(Key(source, z, x, y), tile, EntryOptions);

    public void Invalidate(string source) =>
        // При обновлении данных города можно сбросить кэш конкретного источника
        // Полный сброс — перезапуск сервиса
        _cache.Remove(source);

    private static string Key(string source, int z, int x, int y) =>
        $"{source}/{z}/{x}/{y}";
}
