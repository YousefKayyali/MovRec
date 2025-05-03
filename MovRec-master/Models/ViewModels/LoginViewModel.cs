using System.ComponentModel.DataAnnotations;

namespace MovRec.Models
{
    public class LoginViewModel
    {
        [Required(ErrorMessage = "Username is required")]
        public string username { get; set; }

        [Required]
        [DataType(DataType.Password)]
        public string password { get; set; }
    }
}