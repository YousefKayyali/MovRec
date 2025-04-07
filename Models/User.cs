using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.AspNetCore.Mvc;

namespace MovRec.Models
{
    [Table("users")]
    public class User
    {
        [Key]
        [Column("user_id")]
        public int user_id { get; set; }
        [Remote(action: "VerifyUsername", controller: "Account", ErrorMessage = "Username is already taken")]
        public required string username { get; set; }
        [EmailAddress]
        [Remote(action: "VerifyEmail", controller: "Account", ErrorMessage = "Email is already registered")]
        public required string email { get; set; }
        [DataType(DataType.Password)]
        public required string password { get; set; }
        public string? gener { get; set; }
        [DataType(DataType.Date)]
        [Column(TypeName = "date")] // Explicitly map to PostgreSQL DATE type
        public DateOnly birth_date { get; set; }
        public DateTime create_date { get; set; } = DateTime.UtcNow;
        public bool is_active { get; set; } = true;
        [NotMapped]
        [Compare("password", ErrorMessage = "The password and confirmation password do not match.")]
        public string ConfirmPassword { get; set; }
    }
}