
namespace MovRec.Models
{
    public class HomeViewModel
    {
        public List<Movie> Movies { get; set; } // List of movies
        public List<Genre> Genres { get; set; } // List of genres
        public List<Movie> RecoMovies {get;set;}
    }

    public class Genre
    {
        public string Value { get; set; }
        public string Text { get; set; }
    }
}