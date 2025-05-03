using MovRec.Models;
using System.Collections.Generic;

namespace MovRec.Models.ViewModels
{
    public class MovieDetailsViewModel
    {
        public Movie Movie { get; set; }
        public IEnumerable<Movie> SimilarMovies { get; set; }
        public IEnumerable<string> Genres { get; set; }
        public IEnumerable<SimilarMovieWithScore> SimilarMoviesWithScores { get; set; }
    }

    public class SimilarMovieWithScore
    {
        public Movie Movie { get; set; }
        public decimal Score { get; set; }
    }
}