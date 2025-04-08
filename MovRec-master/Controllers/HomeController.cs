using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Models;
using System.Linq;
using MovRec.Services;

namespace MovRec.Controllers;

public class HomeController : Controller
{
    private readonly ApplicationDbContext _context;
    private readonly IGenreService _genreService;
    public HomeController(ApplicationDbContext context, IGenreService genreService)
    {
        _context = context;
        _genreService = genreService;
    }
    public async Task<IActionResult> Index()
    {
        var topMovies = await _context.Movies
        .Where(m => m.avg_rate != null)
        .OrderByDescending(m => m.avg_rate)
        .Take(35)
        .ToListAsync();

        var recoMovies = await _context.Movies
            .OrderByDescending(m => m.movie_id)
            .Take(35)
            .ToListAsync();
        var model = new HomeViewModel
        {
            Movies = topMovies,
            RecoMovies = recoMovies
        };
        return View(model);

    }


    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
