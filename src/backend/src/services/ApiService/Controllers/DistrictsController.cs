using ApiService.Models;
using ApiService.Services;
using Microsoft.AspNetCore.Mvc;

namespace ApiService.Controllers;

[ApiController]
[Route("api/districts")]
public class DistrictsController(IDistrictService districts) : ControllerBase
{
    [HttpGet("score")]
    public async Task<IActionResult> GetScores(
        [FromQuery] double ecology = 1,
        [FromQuery] double infrastructure = 1,
        [FromQuery] double transport = 1)
    {
        var weights = new DistrictScoreRequest(ecology, infrastructure, transport);
        var result = await districts.GetScoresAsync(weights);
        return Ok(result);
    }

    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(
        int id,
        [FromQuery] double ecology = 1,
        [FromQuery] double infrastructure = 1,
        [FromQuery] double transport = 1)
    {
        var weights = new DistrictScoreRequest(ecology, infrastructure, transport);
        var result = await districts.GetByIdAsync(id, weights);
        return result is null ? NotFound() : Ok(result);
    }
}
