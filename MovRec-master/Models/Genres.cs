using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MovRec.Models;
[Table("genres")]
public class Genres
{
    [Key, Column(Order = 1)]
    public int movie_id { get; set; }

    [Key, Column(Order = 2)]
    public string genre { get; set; }
}