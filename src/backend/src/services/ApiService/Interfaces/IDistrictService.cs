using ApiService.Models;

namespace ApiService.Interfaces;

public interface IDistrictService
{
    Task<IEnumerable<DistrictScore>> GetScoresAsync(DistrictScoreRequest weights);
    Task<DistrictScore?> GetByIdAsync(int id, DistrictScoreRequest weights);
}
