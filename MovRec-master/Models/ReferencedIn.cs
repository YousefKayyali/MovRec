using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MovRec.Models
{
    [Table("referened_in")]
    public class ReferencedIn
    {
        [Key]
        [Column("movie_id")]
        public int movie_id { get; set; }

        [Key]
        [Column("user_id")]
        public int user_id { get; set; }

        // Navigation properties
        public Movie Movie { get; set; }
        public User User { get; set; }
    }
}