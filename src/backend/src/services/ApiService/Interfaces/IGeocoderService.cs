using ApiService.Models;

namespace ApiService.Interfaces;

public interface IGeocoderService
{
    Task<IEnumerable<GeoResult>> SearchAsync(string query);
    Task<GeoResult?> ReverseAsync(double lat, double lng);
}
