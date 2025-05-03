using System.Collections.Generic;
using MovRec.Models;

namespace MovRec.Models.ViewModels
{
    public class HomeViewModel
    {
        public List<Movie> Movies { get; set; } = new List<Movie>();
        public List<Movie> RecoMovies { get; set; } = new List<Movie>();
        public Dictionary<string, List<Movie>> GenreMovies { get; set; } = new Dictionary<string, List<Movie>>();
        public List<string> UserGenres { get; set; } = new List<string>();
        public List<Movie> TopRatedMovies { get; set; } = new List<Movie>();
        public List<Movie> RandomGenre1Movies { get; set; } = new List<Movie>();
        public List<Movie> RandomGenre2Movies { get; set; } = new List<Movie>();
        public List<Movie> LatestReleases { get; set; } = new List<Movie>();
        public string RandomGenre1 { get; set; }
        public string RandomGenre2 { get; set; }
    }
}