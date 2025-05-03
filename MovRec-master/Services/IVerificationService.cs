using System.Threading.Tasks;

namespace MovRec.Services
{
    public interface IVerificationService
    {
        Task<string> GenerateVerificationCodeAsync(int userId, string verificationType);
        Task<bool> VerifyCodeAsync(int userId, string code, string verificationType);
        Task<bool> IsCodeValidAsync(int userId, string code, string verificationType);
    }
}