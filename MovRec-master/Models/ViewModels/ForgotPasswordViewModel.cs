using System.ComponentModel.DataAnnotations;

namespace MovRec.Models
{
    public class ForgotPasswordViewModel
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; }
    }
}