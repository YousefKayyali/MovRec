using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MovRec.Models
{
    [Table("model_recommendation", Schema = "model")]
    public class ModelRecommendations
    {
        [Key]
        [Column("user_id")]
        public int user_id { get; set; }

        [Key]
        [Column("movie_id")]
        public int movie_id { get; set; }

        [Column("rating")]
        public double rating { get; set; }

        [ForeignKey("movie_id")]
        public virtual Movie Movie { get; set; }

        [ForeignKey("user_id")]
        public virtual User User { get; set; }
    }
}