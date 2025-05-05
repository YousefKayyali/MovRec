using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Models;
using MovRec.Models.ViewModels;
using System.Linq;
using MovRec.Services;
using MovRec.Filters;
using Microsoft.AspNetCore.Authorization;

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
        // Get top rated movies
        var topRatedMovies = await _context.Movies
            .Where(m => m.avg_rate != null)
            .OrderByDescending(m => m.avg_rate)
            .Take(35)
            .ToListAsync();

        // Get two random genres
        var allGenres = await _context.Genres
            .Select(g => g.genre)
            .Distinct()
            .ToListAsync();

        var random = new Random();
        var randomGenres = allGenres.OrderBy(x => random.Next()).Take(2).ToList();
        var randomGenre1 = randomGenres[0];
        var randomGenre2 = randomGenres[1];

        // Get movies for random genres
        var genre1Movies = await _context.Movies
            .Where(m => _context.Genres
                .Where(g => g.genre == randomGenre1)
                .Select(g => g.movie_id)
                .Contains(m.movie_id))
            .OrderByDescending(m => m.avg_rate)
            .Take(35)
            .ToListAsync();

        var genre2Movies = await _context.Movies
            .Where(m => _context.Genres
                .Where(g => g.genre == randomGenre2)
                .Select(g => g.movie_id)
                .Contains(m.movie_id))
            .OrderByDescending(m => m.avg_rate)
            .Take(35)
            .ToListAsync();

        // Get latest releases (2022-2023)
        var latestReleases = await _context.Movies
            .Where(m => m.release_date.Year >= 2022)
            .OrderByDescending(m => m.avg_rate)
            .Take(35)
            .ToListAsync();

        var model = new HomeViewModel
        {
            TopRatedMovies = topRatedMovies,
            RandomGenre1Movies = genre1Movies,
            RandomGenre2Movies = genre2Movies,
            LatestReleases = latestReleases,
            RandomGenre1 = randomGenre1,
            RandomGenre2 = randomGenre2
        };
        return View(model);
    }

    [AuthorizeUser]
    public async Task<IActionResult> UserHome()
    {
        var userId = HttpContext.Session.GetInt32("UserId");
        if (userId == null)
        {
            return RedirectToAction("Login", "Account");
        }

        // Get user's selected genres
        var user = await _context.Users.FindAsync(userId);
        var userGenres = user.gener?.Split(',').ToList() ?? new List<string>();

        // Format genre names for database comparison
        var formattedUserGenres = userGenres.Select(g =>
        {
            if (g == "Science Fiction")
                return "ScienceFiction";
            if (g == "TV Movie")
                return "TVMovie";
            return g;
        }).ToList();

        // Get recommended movies (top rated overall)
        var recommendedMovies = await _context.Movies
            .OrderByDescending(m => m.avg_rate)
            .Take(35)
            .ToListAsync();

        // Keep track of all movies that have been used in any carousel
        var usedMovieIds = new HashSet<int>(recommendedMovies.Select(m => m.movie_id));

        // Get top movies for each of user's selected genres, excluding any previously used movies
        var genreMovies = new Dictionary<string, List<Movie>>();
        foreach (var genre in formattedUserGenres)
        {
            // Get more movies than we need since some might be filtered out
            var moviesInGenre = await _context.Movies
                .Where(m => _context.Genres
                    .Where(g => g.genre.ToLower() == genre.ToLower())
                    .Select(g => g.movie_id)
                    .Contains(m.movie_id))
                .Where(m => !usedMovieIds.Contains(m.movie_id)) // Exclude any previously used movies
                .OrderByDescending(m => m.avg_rate)
                .Take(35)
                .ToListAsync();

            // Add these movies to the used set
            foreach (var movie in moviesInGenre)
            {
                usedMovieIds.Add(movie.movie_id);
            }

            // Store with the original genre name for display
            var displayGenre = userGenres[formattedUserGenres.IndexOf(genre)];
            genreMovies[displayGenre] = moviesInGenre;
        }

        // Get latest releases (2022-2023)
        var latestReleases = await _context.Movies
            .Where(m => m.release_date.Year >= 2022)
            .OrderByDescending(m => m.avg_rate)
            .Take(35)
            .ToListAsync();

        var model = new HomeViewModel
        {
            RecoMovies = recommendedMovies,
            GenreMovies = genreMovies,
            UserGenres = userGenres,
            LatestReleases = latestReleases
        };

        return View(model);
    }

    public async Task<IActionResult> Search(string query)
    {
        if (string.IsNullOrWhiteSpace(query))
        {
            return RedirectToAction("Index");
        }

        var movies = await _context.Movies
            .Where(m => m.title.ToLower().Contains(query.ToLower()))
            .OrderByDescending(m => m.avg_rate)
            .ToListAsync();

        var model = new HomeViewModel
        {
            Movies = movies
        };

        return View("SearchResults", model);
    }

    public async Task<IActionResult> Autocomplete(string term)
    {
        if (string.IsNullOrWhiteSpace(term))
        {
            return Json(new List<string>());
        }

        var suggestions = await _context.Movies
            .Where(m => m.title.ToLower().Contains(term.ToLower()))
            .OrderByDescending(m => m.avg_rate)
            .Take(7)
            .Select(m => m.title)
            .ToListAsync();

        return Json(suggestions);
    }

    [AuthorizeUser]
    public async Task<IActionResult> Recommendations()
    {
        var userId = HttpContext.Session.GetInt32("UserId");
        if (userId == null)
        {
            return RedirectToAction("Login", "Account");
        }

        // Get personalized recommendations from both user and model recommendations
        var userRecommendations = await _context.UserRecommendations
            .Where(ur => ur.user_id == userId)
            .Include(ur => ur.Movie)
            .Select(ur => ur.Movie)
            .ToListAsync();

        var modelRecommendations = await _context.ModelRecommendations
            .Where(mr => mr.user_id == userId)
            .Include(mr => mr.Movie)
            .Select(mr => mr.Movie)
            .ToListAsync();

        // Combine both types of recommendations
        var recommendedMovies = userRecommendations.Union(modelRecommendations).ToList();

        // If no personalized recommendations, get movies from user's chosen genres
        if (!recommendedMovies.Any())
        {
            // Get user's selected genres
            var user = await _context.Users.FindAsync(userId);
            var userGenres = user.gener?.Split(',').ToList() ?? new List<string>();

            // Format genre names for database comparison
            var formattedUserGenres = userGenres.Select(g =>
            {
                if (g == "Science Fiction")
                    return "ScienceFiction";
                if (g == "TV Movie")
                    return "TVMovie";
                return g;
            }).ToList();

            // Get movies from user's chosen genres
            recommendedMovies = await _context.Movies
                .Where(m => _context.Genres
                    .Where(g => formattedUserGenres.Contains(g.genre))
                    .Select(g => g.movie_id)
                    .Contains(m.movie_id))
                .Take(200)
                .ToListAsync();
        }

        // Shuffle the movies regardless of their source
        var random = new Random();
        recommendedMovies = recommendedMovies.OrderBy(x => random.Next()).ToList();

        var viewModel = new HomeViewModel
        {
            Movies = recommendedMovies
        };
        return View(viewModel);
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
