using System.Threading.Tasks;

namespace MovRec.Services
{
    public interface IEmailService
    {
        Task SendVerificationEmailAsync(string email, string verificationCode, string verificationType);
        Task SendPasswordResetEmailAsync(string email, string resetCode);
    }
}