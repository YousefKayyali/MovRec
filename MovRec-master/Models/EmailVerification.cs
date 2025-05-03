using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MovRec.Models
{
    [Table("email_verifications")]
    public class EmailVerification
    {
        [Key]
        public int verification_id { get; set; }

        [Required]
        public int user_id { get; set; }

        [Required]
        public string verification_code { get; set; }

        [Required]
        public DateTime created_at { get; set; } = DateTime.UtcNow;

        [Required]
        public DateTime expires_at { get; set; }

        [Required]
        public bool is_used { get; set; } = false;

        [Required]
        public string verification_type { get; set; } // "signup" or "password_reset"

        [ForeignKey("user_id")]
        public virtual User User { get; set; }
    }
}