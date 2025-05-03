using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Models;
using MovRec.Models.ViewModels;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Collections.Generic;
using Npgsql;
using MovRec.Helpers;

namespace MovRec.Controllers
{
    public class MoviesController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly string pythonPath = "python"; // Assuming python is in PATH, otherwise use full path

        public MoviesController(ApplicationDbContext context)
        {
            _context = context;
        }

        private async Task RunPythonScript(int userId, int movieId, double rating)
        {
            try
            {
                var scriptPath = "after_rating.py";
                var arguments = $"{userId} {movieId} {rating}";

                var (exitCode, output, error) = await PythonRunner.RunAsync(scriptPath, arguments);

                if (exitCode != 0)
                {

                    Console.WriteLine($"Python script failed with exit code {exitCode}");
                    Console.WriteLine($"Error: {error}");
                }
                else
                {
                    Console.WriteLine($"Python script output: {output}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error executing script: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
            }
        }

        // Action method to fetch movie details
        public async Task<IActionResult> Details(int id)
        {
            var movie = await _context.Movies.FirstOrDefaultAsync(m => m.movie_id == id);
            if (movie == null)
            {
                return NotFound();
            }

            // Get movie genres
            var genres = await _context.Genres
                .Where(g => g.movie_id == id)
                .Select(g => g.genre)
                .ToListAsync();

            // Get similar movies from SimilarMovie table
            var similarMoviesWithScores = await _context.SimilarMovies
                .Where(sm => sm.movie_id == id)
                .Include(sm => sm.SimilarMovieNavigation)
                .OrderByDescending(sm => sm.score)
                .Select(sm => new SimilarMovieWithScore
                {
                    Movie = sm.SimilarMovieNavigation,
                    Score = sm.score
                })
                .Take(30)
                .ToListAsync();

            // Check if movie is in user's watchlist and get user's rating
            var userId = HttpContext.Session.GetInt32("UserId");
            double? userRating = null;
            bool isInWatchlist = false;

            if (userId != null)
            {
                isInWatchlist = await _context.ReferencedIn
                    .AnyAsync(r => r.movie_id == id && r.user_id == userId.Value);

                var watchEvent = await _context.WatchEvents
                    .FirstOrDefaultAsync(we => we.movie_id == id && we.user_id == userId.Value);

                userRating = watchEvent?.rating;
            }

            ViewBag.IsInWatchlist = isInWatchlist;
            ViewBag.UserRating = userRating;

            var viewModel = new MovieDetailsViewModel
            {
                Movie = movie,
                Genres = genres,
                SimilarMoviesWithScores = similarMoviesWithScores
            };

            return View(viewModel);
        }

        [HttpPost]
        public async Task<IActionResult> AddToWatchlist(int movieId)
        {
            var userId = HttpContext.Session.GetInt32("UserId");
            if (userId == null)
            {
                return Json(new { success = false, message = "User not logged in" });
            }

            // Check if movie is already in watchlist
            var existingEntry = await _context.ReferencedIn
                .FirstOrDefaultAsync(r => r.movie_id == movieId && r.user_id == userId.Value);

            if (existingEntry == null)
            {
                // Add to watchlist
                var newEntry = new ReferencedIn
                {
                    movie_id = movieId,
                    user_id = userId.Value
                };

                _context.ReferencedIn.Add(newEntry);
                await _context.SaveChangesAsync();
                return Json(new { success = true, action = "add" });
            }
            else
            {
                // Remove from watchlist
                _context.ReferencedIn.Remove(existingEntry);
                await _context.SaveChangesAsync();
                return Json(new { success = true, action = "remove" });
            }
        }

        [HttpPost]
        public async Task<IActionResult> RateMovie(int movieId, double rating)
        {

            var userId = HttpContext.Session.GetInt32("UserId");
            if (userId == null)
            {
                return Json(new { success = false, message = "User not logged in" });
            }

            try
            {
                var watchEvent = await _context.WatchEvents
                    .FirstOrDefaultAsync(we => we.movie_id == movieId && we.user_id == userId);

                if (rating == 0) // Remove rating case
                {
                    if (watchEvent != null)
                    {
                        // Get the latest rated movie for this user
                        var latestRatedMovie = await _context.WatchEvents
                            .Where(we => we.user_id == userId.Value && we.rating != null)
                            .OrderByDescending(we => we.watch_date)
                            .FirstOrDefaultAsync();

                        // If the removed rating is for the latest rated movie
                        if (latestRatedMovie != null && latestRatedMovie.movie_id == movieId)
                        {
                            // Run the SQL query to restore from backup
                            var connectionString = _context.Database.GetConnectionString();
                            using (var connection = new NpgsqlConnection(connectionString))
                            {

                                await connection.OpenAsync();
                                using (var command = new NpgsqlCommand())
                                {
                                    command.Connection = connection;
                                    command.CommandText = @"
                                        DELETE FROM model.user_latent_attributes
                                        WHERE user_id = @userId;

                                        INSERT INTO model.user_latent_attributes (
                                            user_id, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10,
                                            l11, l12, l13, l14, l15, l16, l17, l18, l19, l20,
                                            l21, l22, l23, l24, l25, l26, l27, l28, l29, l30,
                                            l31, l32, l33, l34, l35, l36, l37, l38, l39, l40,
                                            l41, l42, l43, l44, l45, l46, l47, l48, l49, l50,
                                            l51, l52, l53, l54, l55, l56, l57, l58, l59, l60,
                                            l61, l62, l63, l64, l65, l66, l67, l68, l69, l70,
                                            l71, l72, l73, l74, l75, l76, l77, l78, l79, l80,
                                            l81, l82, l83, l84, l85, l86, l87, l88, l89, l90,
                                            l91, l92, l93, l94, l95, l96, l97, l98, l99, l100
                                        )
                                        SELECT user_id, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10,
                                               l11, l12, l13, l14, l15, l16, l17, l18, l19, l20,
                                               l21, l22, l23, l24, l25, l26, l27, l28, l29, l30,
                                               l31, l32, l33, l34, l35, l36, l37, l38, l39, l40,
                                               l41, l42, l43, l44, l45, l46, l47, l48, l49, l50,
                                               l51, l52, l53, l54, l55, l56, l57, l58, l59, l60,
                                               l61, l62, l63, l64, l65, l66, l67, l68, l69, l70,
                                               l71, l72, l73, l74, l75, l76, l77, l78, l79, l80,
                                               l81, l82, l83, l84, l85, l86, l87, l88, l89, l90,
                                               l91, l92, l93, l94, l95, l96, l97, l98, l99, l100
                                        FROM model.user_latent_attributes_backups
                                        WHERE user_id = @userId;";
                                    command.Parameters.AddWithValue("@userId", userId.Value);
                                    await command.ExecuteNonQueryAsync();
                                }
                            }
                        }

                        _context.WatchEvents.Remove(watchEvent);
                        await _context.SaveChangesAsync();
                    }
                    return Json(new { success = true });
                }

                if (watchEvent == null)
                {
                    watchEvent = new WatchEvent
                    {
                        movie_id = movieId,
                        user_id = userId.Value,
                        watch_date = DateTime.UtcNow,
                        rating = rating
                    };
                    _context.WatchEvents.Add(watchEvent);
                }
                else
                {
                    watchEvent.rating = rating;
                    watchEvent.watch_date = DateTime.UtcNow;
                }

                await _context.SaveChangesAsync();

                // Check if user's rating count is a multiple of 10
                var ratedMoviesCount = await _context.WatchEvents
                    .CountAsync(we => we.user_id == userId.Value && we.rating != null);

                if (ratedMoviesCount % 10 == 0)
                {
                    // Run model.py script with only userId
                    var scriptPath = "model.py";
                    var arguments = $"{userId} {movieId} {rating}";

                    var (exitCode, output, error) = await PythonRunner.RunAsync(scriptPath, arguments);

                    if (exitCode != 0)
                    {
                        Console.WriteLine($"[model.py] Script failed with exit code {exitCode}");
                        Console.WriteLine($"[model.py] Error: {error}");
                    }
                    else
                    {
                        Console.WriteLine($"[model.py] Script finished execution");
                        Console.WriteLine($"[model.py] Output: {output}");
                    }
                }

                // Check if user's rating count is a multiple of 17
                if (ratedMoviesCount % 17 == 0)
                {
                    // Run user-to-user recommendation script with original arguments
                    var scriptPath = "user_to_user_lr.py";
                    var arguments = $"{userId}";

                    var (exitCode, output, error) = await PythonRunner.RunAsync(scriptPath, arguments);

                    if (exitCode != 0)
                    {
                        Console.WriteLine($"[user_to_user_lr.py] Script failed with exit code {exitCode}");
                        Console.WriteLine($"[user_to_user_lr.py] Error: {error}");
                    }
                    else
                    {
                        Console.WriteLine($"[user_to_user_lr.py] Script finished execution");
                        Console.WriteLine($"[user_to_user_lr.py] Output: {output}");
                    }
                }

                // Run Python script after successfully saving the rating with original arguments
                await RunPythonScript(userId.Value, movieId, rating);

                return Json(new { success = true });
            }
            catch (Exception ex)
            {
                var innerMessage = ex.InnerException?.Message ?? "No inner exception";
                var stackTrace = ex.StackTrace;
                return Json(new
                {
                    success = false,
                    message = $"Error: {ex.Message}",
                    innerException = innerMessage,
                    stackTrace = stackTrace
                });
            }
        }

        public async Task<IActionResult> Watchlist()
        {
            var userId = HttpContext.Session.GetInt32("UserId");
            if (userId == null)
            {
                return RedirectToAction("Login", "Account");
            }

            var watchlistMovies = await _context.ReferencedIn
                .Where(r => r.user_id == userId.Value)
                .Select(r => r.Movie)
                .ToListAsync();

            return View(watchlistMovies);
        }

        [HttpPost]
        public async Task<IActionResult> ClearWatchlist()
        {
            var userId = HttpContext.Session.GetInt32("UserId");
            if (userId == null)
            {
                return Json(new { success = false, message = "User not logged in" });
            }

            try
            {
                var watchlistItems = await _context.ReferencedIn
                    .Where(r => r.user_id == userId.Value)
                    .ToListAsync();

                _context.ReferencedIn.RemoveRange(watchlistItems);
                await _context.SaveChangesAsync();

                return Json(new { success = true });
            }
            catch (Exception ex)
            {
                return Json(new { success = false, message = ex.Message });
            }
        }

        public async Task<IActionResult> Ratings()
        {
            var userId = HttpContext.Session.GetInt32("UserId");
            if (userId == null)
            {
                return RedirectToAction("Login", "Account");
            }

            var ratedMovies = await _context.WatchEvents
                .Where(w => w.user_id == userId.Value && w.rating != null)
                .Include(w => w.Movie)
                .OrderByDescending(w => w.watch_date)
                .Select(w => new MovieWithRating
                {
                    Movie = w.Movie,
                    Rating = w.rating.Value
                })
                .ToListAsync();

            return View(ratedMovies);
        }

        public async Task<IActionResult> AdvancedSearch(string searchQuery, string[] genres, int[] decades)
        {
            // Get all unique genres for the checkboxes
            var allGenres = await _context.Genres
                .Select(g => g.genre)
                .Distinct()
                .OrderBy(g => g)
                .ToListAsync();

            ViewBag.Genres = allGenres;
            ViewBag.SearchQuery = searchQuery;
            ViewBag.SelectedGenres = genres?.ToList() ?? new List<string>();
            ViewBag.SelectedDecades = decades?.ToList() ?? new List<int>();

            // Only perform search if there's at least one filter applied
            if (string.IsNullOrEmpty(searchQuery) && (genres == null || genres.Length == 0) && (decades == null || decades.Length == 0))
            {
                return View(new List<Movie>());
            }

            var query = _context.Movies.AsQueryable();

            // Apply search query filter
            if (!string.IsNullOrEmpty(searchQuery))
            {
                query = query.Where(m => m.title.ToLower().Contains(searchQuery.ToLower()));
            }

            // Apply genre filter
            if (genres != null && genres.Length > 0)
            {
                var selectedGenres = genres.ToList();
                var movieIdsWithGenres = await _context.Genres
                    .Where(g => selectedGenres.Contains(g.genre))
                    .Select(g => g.movie_id)
                    .ToListAsync();

                query = query.Where(m => movieIdsWithGenres.Contains(m.movie_id));
            }

            // Apply decade filter
            if (decades != null && decades.Length > 0)
            {
                var selectedDecades = decades.ToList();
                var years = selectedDecades.SelectMany(d => Enumerable.Range(d, 10)).ToList();
                query = query.Where(m => years.Contains(m.release_date.Year));
            }

            // Sort by rating in descending order
            query = query.OrderByDescending(m => m.avg_rate);

            var movies = await query.ToListAsync();
            return View(movies);
        }
    }
}
