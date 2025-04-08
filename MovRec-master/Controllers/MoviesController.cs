using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Models;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;

namespace MovRec.Controllers
{
    public class MoviesController : Controller
    {
        private readonly ApplicationDbContext _context;

        public MoviesController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Action method to fetch movie details
        public async Task<IActionResult> Details(int id)
        {
            var movie = _context.Movies.FirstOrDefault(m => m.movie_id == id);
            if (movie == null)
            {
                return NotFound();
            }
            int userId = int.Parse(User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? "0");
            // Get user rating from watch_events
            var watchEvent = await _context.WatchEvents
                .FirstOrDefaultAsync(w => w.movie_id == id && w.user_id == userId);
            var viewModel = new MovieDetailsViewModel
            {
                Movie = movie,
                UserRating = watchEvent?.rating
            };

            return View(viewModel);
        }

        [HttpPost]
    public async Task<IActionResult> RateMovie(int movieId, int rating)
    {
        int userId = int.Parse(User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? "0");

        var watchEvent = await _context.WatchEvents
            .FirstOrDefaultAsync(w => w.movie_id == movieId && w.user_id == userId);

        if (watchEvent == null)
        {
            watchEvent = new WatchEvent
            {
                movie_id = movieId,
                user_id = userId,
                watch_date = DateTime.Now,
                rating = rating
            };
            _context.WatchEvents.Add(watchEvent);
        }
        else
        {
            watchEvent.rating = rating;
        }

        await _context.SaveChangesAsync();
        return Json(new { success = true });
    }
    }
}
