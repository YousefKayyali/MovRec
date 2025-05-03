using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MovRec.Models
{
    [Table("user_recommendation", Schema = "model")]
    public class UserRecommendation
    {
        [Key]
        [Column("user_id")]
        public int user_id { get; set; }

        [Key]
        [Column("movie_id")]
        public int movie_id { get; set; }

        [Column("avg_rate")]
        public double avg_rate { get; set; }

        [ForeignKey("movie_id")]
        public virtual Movie Movie { get; set; }

        [ForeignKey("user_id")]
        public virtual User User { get; set; }
    }
}