using ApiService.Models;
using Dapper;
using Npgsql;
using ApiService.Interfaces;

namespace ApiService.Services;

public class DistrictService(NpgsqlDataSource db) : IDistrictService
{
    public async Task<IEnumerable<DistrictScore>> GetScoresAsync(DistrictScoreRequest w)
    {
        await using var conn = await db.OpenConnectionAsync();
        return await conn.QueryAsync<DistrictScore>(BuildQuery(), BuildParams(w));
    }

    public async Task<DistrictScore?> GetByIdAsync(int id, DistrictScoreRequest w)
    {
        await using var conn = await db.OpenConnectionAsync();
        var p = BuildParams(w);
        p.Add("id", id);
        return await conn.QueryFirstOrDefaultAsync<DistrictScore>(
            BuildQuery() + " AND h.id = @id", p);
    }

    private static string BuildQuery() => """
        SELECT
            h.id                                                         AS "Id",
            h.name                                                       AS "Name",
            COALESCE(h.ecology_score, 0)                                 AS "EcologyScore",
            COALESCE(h.infrastructure_score, 0)                          AS "InfrastructureScore",
            COALESCE(h.transport_score, 0)                               AS "TransportScore",
            ROUND((
                COALESCE(h.ecology_score, 0)       * @ecology +
                COALESCE(h.infrastructure_score, 0)* @infrastructure +
                COALESCE(h.transport_score, 0)     * @transport
            )::numeric, 2)                                               AS "OverallScore",
            ST_Y(ST_Centroid(h.geometry))                                AS "Lat",
            ST_X(ST_Centroid(h.geometry))                                AS "Lng"
        FROM hex_grid h
        WHERE h.geometry IS NOT NULL
        ORDER BY "OverallScore" DESC
        """;

    private static DynamicParameters BuildParams(DistrictScoreRequest w)
    {
        var total = w.EcologyWeight + w.InfrastructureWeight + w.TransportWeight;
        if (total == 0) total = 1;
        var p = new DynamicParameters();
        p.Add("ecology",        w.EcologyWeight        / total);
        p.Add("infrastructure", w.InfrastructureWeight / total);
        p.Add("transport",      w.TransportWeight      / total);
        return p;
    }
}
