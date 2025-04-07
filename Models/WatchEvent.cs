using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.AspNetCore.Mvc;

namespace MovRec.Models
{
    [Table("watch_events")]
    public class WatchEvent
    {
        [Key, Column(Order = 1)]
        public int movie_id { get; set; }
        [Key, Column(Order = 2)]
        public int user_id { get; set; }
        public DateTime watch_date { get; set; } = DateTime.Now;
        public string? review { get; set; }
        [Range(1, 10)]
        public int? rating { get; set; }
        [ForeignKey("movie_id")]
        public virtual Movie Movie { get; set; }
        [ForeignKey("user_id")]
        public virtual User User { get; set; }
    }
}