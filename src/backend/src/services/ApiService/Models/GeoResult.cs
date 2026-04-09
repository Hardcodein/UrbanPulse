namespace ApiService.Models;

public record GeoResult(
    string DisplayName,
    double Lat,
    double Lng,
    string Type
);
