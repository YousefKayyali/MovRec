using System.ComponentModel.DataAnnotations;

namespace MovRec.Models.ViewModels
{
    public class CategoriesViewModel
    {
        public List<string> SelectedCategories { get; set; } = new List<string>();

        public List<string> AvailableCategories { get; set; } = new List<string>
        {
            "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
            "Drama", "Family", "Fantasy", "History", "Horror", "Music",
            "Mystery", "Romance", "Science Fiction", "TV Movie", "Thriller", "War", "Western"
        };
    }
}