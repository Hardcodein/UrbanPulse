using System.Text.Json;
using ApiService.Models;
using Microsoft.Extensions.Caching.Memory;
using ApiService.Interfaces;

namespace ApiService.Services;

public class GeocoderService(HttpClient http, IMemoryCache cache) : IGeocoderService
{
    private static readonly JsonSerializerOptions JsonOpts = new() { PropertyNameCaseInsensitive = true };

    public async Task<IEnumerable<GeoResult>> SearchAsync(string query)
    {
        var key = $"search:{query.ToLowerInvariant()}";
        if (cache.TryGetValue(key, out IEnumerable<GeoResult>? cached))
            return cached!;

        var url = $"/search?q={Uri.EscapeDataString(query)}&format=json&limit=5&countrycodes=ru";
        var json = await http.GetStringAsync(url);
        var items = JsonSerializer.Deserialize<NominatimResult[]>(json, JsonOpts) ?? [];

        var results = items.Select(r => new GeoResult(
            r.DisplayName, double.Parse(r.Lat), double.Parse(r.Lon), r.Type)).ToList();

        cache.Set(key, results, TimeSpan.FromHours(24));
        return results;
    }

    public async Task<GeoResult?> ReverseAsync(double lat, double lng)
    {
        var key = $"reverse:{lat:F4}:{lng:F4}";
        if (cache.TryGetValue(key, out GeoResult? cached))
            return cached;

        var url = $"/reverse?lat={lat}&lon={lng}&format=json";
        var json = await http.GetStringAsync(url);
        var r = JsonSerializer.Deserialize<NominatimResult>(json, JsonOpts);
        if (r is null) return null;

        var result = new GeoResult(r.DisplayName, double.Parse(r.Lat), double.Parse(r.Lon), r.Type);
        cache.Set(key, result, TimeSpan.FromHours(24));
        return result;
    }

    private record NominatimResult(
        string DisplayName,
        string Lat,
        string Lon,
        string Type);
}
