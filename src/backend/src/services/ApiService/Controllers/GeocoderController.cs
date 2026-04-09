using ApiService.Services;
using Microsoft.AspNetCore.Mvc;

namespace ApiService.Controllers;

[ApiController]
[Route("api/search")]
public class GeocoderController(IGeocoderService geocoder) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> Search([FromQuery] string q)
    {
        if (string.IsNullOrWhiteSpace(q))
            return BadRequest("Параметр q обязателен");

        var results = await geocoder.SearchAsync(q);
        return Ok(results);
    }

    [HttpGet("reverse")]
    public async Task<IActionResult> Reverse([FromQuery] double lat, [FromQuery] double lng)
    {
        var result = await geocoder.ReverseAsync(lat, lng);
        return result is null ? NotFound() : Ok(result);
    }
}
