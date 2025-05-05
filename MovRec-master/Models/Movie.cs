using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MovRec.Models;
[Table("movies")]
public class Movie
{
    [Key]
    [Column("movie_id")]
    public int movie_id { get; set; }
    public string? title { get; set; }
    public string? over_review { get; set; }
    public int? runtime { get; set; }
    public DateOnly release_date { get; set; }
    public string? casts { get; set; }
    public bool? adult { get; set; }
    public string? director { get; set; }
    public string? production_companies { get; set; }
    public string? production_countries { get; set; }
    public double? avg_rate { get; set; }
    public double? public_rating { get; set; }
}
