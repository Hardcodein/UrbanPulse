namespace ApiService.Models;

public record DistrictScore(
    int Id,
    string Name,
    double EcologyScore,
    double InfrastructureScore,
    double TransportScore,
    double OverallScore,
    double Lat,
    double Lng
);

public record DistrictScoreRequest(
    double EcologyWeight,
    double InfrastructureWeight,
    double TransportWeight
);
