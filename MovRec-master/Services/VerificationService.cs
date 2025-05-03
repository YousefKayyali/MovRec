using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Models;

namespace MovRec.Services
{
    public class VerificationService : IVerificationService
    {
        private readonly ApplicationDbContext _context;
        private readonly IEmailService _emailService;

        public VerificationService(ApplicationDbContext context, IEmailService emailService)
        {
            _context = context;
            _emailService = emailService;
        }

        public async Task<string> GenerateVerificationCodeAsync(int userId, string verificationType)
        {
            // Generate a 6-digit code
            var random = new Random();
            var code = random.Next(100000, 999999).ToString();

            // Create verification record
            var verification = new EmailVerification
            {
                user_id = userId,
                verification_code = code,
                created_at = DateTime.UtcNow,
                expires_at = DateTime.UtcNow.AddHours(1), // Code expires in 1 hour
                is_used = false,
                verification_type = verificationType
            };

            _context.EmailVerifications.Add(verification);
            await _context.SaveChangesAsync();

            // Get user email and send verification code in the background
            var user = await _context.Users.FindAsync(userId);
            if (user != null)
            {
                // Fire and forget the email sending
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await _emailService.SendVerificationEmailAsync(user.email, code, verificationType);
                    }
                    catch (Exception ex)
                    {
                        // Log the error but don't throw it
                        Console.WriteLine($"Error sending verification email: {ex.Message}");
                    }
                });
            }

            return code;
        }

        public async Task<bool> VerifyCodeAsync(int userId, string code, string verificationType)
        {
            var verification = await _context.EmailVerifications
                .Where(v => v.user_id == userId &&
                           v.verification_code == code &&
                           v.verification_type == verificationType &&
                           !v.is_used &&
                           v.expires_at > DateTime.UtcNow)
                .FirstOrDefaultAsync();

            if (verification != null)
            {
                verification.is_used = true;
                await _context.SaveChangesAsync();
                return true;
            }

            return false;
        }

        public async Task<bool> IsCodeValidAsync(int userId, string code, string verificationType)
        {
            return await _context.EmailVerifications
                .AnyAsync(v => v.user_id == userId &&
                             v.verification_code == code &&
                             v.verification_type == verificationType &&
                             !v.is_used &&
                             v.expires_at > DateTime.UtcNow);
        }
    }
}