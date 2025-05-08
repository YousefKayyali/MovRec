using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Services;
using Microsoft.AspNetCore.Authentication.Cookies;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
// Add services to the container.
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString).LogTo(Console.WriteLine, LogLevel.Information));

builder.Services.AddControllersWithViews();

builder.Services.AddScoped<IGenreService, GenreService>();

builder.Services.AddHttpContextAccessor();

builder.Services.AddResponseCompression();

// Add email service
builder.Services.AddScoped<IEmailService>(provider =>
    new EmailService(
        builder.Configuration["EmailSettings:SmtpServer"],
        int.Parse(builder.Configuration["EmailSettings:SmtpPort"]),
        builder.Configuration["EmailSettings:SmtpUsername"],
        builder.Configuration["EmailSettings:SmtpPassword"],
        builder.Configuration["EmailSettings:FromEmail"]
    )
);

// Add verification service
builder.Services.AddScoped<IVerificationService, VerificationService>();

// Add authentication
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/Account/Login";
        options.LogoutPath = "/Account/Logout";
        options.AccessDeniedPath = "/Account/AccessDenied";
    });

// Add session
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(45);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
    options.Cookie.Name = ".MovRec.Session";
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseRouting();
app.UseSession();
app.UseResponseCompression();
app.UseAuthentication();
app.UseAuthorization();

app.UseStaticFiles(new StaticFileOptions
{
    OnPrepareResponse = ctx =>
    {
        // Set Cache-Control header to cache static files for 1 year
        ctx.Context.Response.Headers.Append("Cache-Control", "public,max-age=31536000");
    }
});

app.MapStaticAssets();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}")
    .WithStaticAssets();


app.Run();
