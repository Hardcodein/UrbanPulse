using TileService.Caching;
using TileService.Config;
using TileService.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

var connString = builder.Configuration.GetConnectionString("Db")
    ?? throw new InvalidOperationException("ConnectionStrings:Db не задана");

builder.Services.AddNpgsqlDataSource(connString);

builder.Services.AddSingleton<TileLayerConfig>();

builder.Services.AddMemoryCache(opt => opt.SizeLimit = 50_000);
builder.Services.AddSingleton<TileCache>();

builder.Services.AddScoped<ITileService, PostgresTileService>();

builder.Services.AddCors(opt => opt.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();

app.UseCors();
app.MapControllers();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

app.Run();
