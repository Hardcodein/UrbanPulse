using ApiService.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

var connString = builder.Configuration.GetConnectionString("Db")
    ?? throw new InvalidOperationException("ConnectionStrings:Db не задана");

builder.Services.AddNpgsqlDataSource(connString);

builder.Services.AddMemoryCache(opt => opt.SizeLimit = 10_000);

builder.Services.AddScoped<IDistrictService, DistrictService>();
builder.Services.AddScoped<IGeocoderService, GeocoderService>();

builder.Services.AddHttpClient<IGeocoderService, GeocoderService>(client =>
{
    var nominatimUrl = builder.Configuration["Nominatim:BaseUrl"]
        ?? "https://nominatim.openstreetmap.org";
    client.BaseAddress = new Uri(nominatimUrl);
    client.DefaultRequestHeaders.Add("User-Agent", "UrbanPulse/1.0");
});

builder.Services.AddCors(opt => opt.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();

app.UseCors();
app.MapControllers();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

app.Run();
