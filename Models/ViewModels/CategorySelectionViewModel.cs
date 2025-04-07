using MovRec.Models;

public class CategorySelectionViewModel
{
    public List<Genre> AvailableGenres { get; set; }
    public List<string> SelectedGenres { get; set; } = new List<string>();
}