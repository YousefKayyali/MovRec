using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MovRec.Controllers;
using MovRec.data;
using MovRec.Models;

namespace MovRec.Services
{
    public class GenreService : IGenreService
    {
        private readonly ApplicationDbContext _context;

        public GenreService(ApplicationDbContext context)
        {
            _context = context;
        }

        public List<Genre> GetAvailableGenres()
        {
            // Get unique genres from the database
            var uniqueGenres = _context.Genres
                .Select(g => g.genre)
                .Distinct()
                .OrderBy(g => g)
                .ToList();

            // Convert to Genre objects
            return uniqueGenres.Select(g => new Genre
            {
                Value = g.ToLower(),
                Text = g
            }).ToList();
        }

        public async Task<bool> SaveUserGenres(int userId, List<string> selectedGenres)
        {
            try
            {
                var user = await _context.Users.FindAsync(userId);
                if (user == null) return false;

                // Store as comma-separated string
                user.gener = string.Join(",", selectedGenres);

                await _context.SaveChangesAsync();
                return true;
            }
            catch
            {
                return false;
            }
        }

        public async Task<List<string>> GetUserGenres(int userId)
        {
            var user = await _context.Users.FindAsync(userId);
            if (user?.gener == null) return new List<string>();

            return user.gener.Split(',').ToList();
        }
    }
}