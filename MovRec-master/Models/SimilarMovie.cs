using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MovRec.Models;

[Table("similar_movies")]
public class SimilarMovie
{
    [Key]
    [Column("movie_id")]
    public int movie_id { get; set; }

    [Key]
    [Column("similer_movie_id")]
    public int similer_movie_id { get; set; }

    [Column("score")]
    public decimal score { get; set; }

    [ForeignKey("movie_id")]
    public Movie Movie { get; set; }

    [ForeignKey("similer_movie_id")]
    public Movie SimilarMovieNavigation { get; set; }
}
