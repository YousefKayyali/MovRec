using System.Net.Mail;
using System.Threading.Tasks;
using System.Net.Mime;

namespace MovRec.Services
{
    public class EmailService : IEmailService
    {
        private readonly string _smtpServer;
        private readonly int _smtpPort;
        private readonly string _smtpUsername;
        private readonly string _smtpPassword;
        private readonly string _fromEmail;
        private readonly string _fromName;

        public EmailService(string smtpServer, int smtpPort, string smtpUsername, string smtpPassword, string fromEmail)
        {
            _smtpServer = smtpServer;
            _smtpPort = smtpPort;
            _smtpUsername = smtpUsername;
            _smtpPassword = smtpPassword;
            _fromEmail = fromEmail;
            _fromName = "MovRec"; // Your application name
        }

        public async Task SendVerificationEmailAsync(string email, string verificationCode, string verificationType)
        {
            using (var client = new SmtpClient(_smtpServer, _smtpPort))
            {
                client.UseDefaultCredentials = false;
                client.Credentials = new System.Net.NetworkCredential(_smtpUsername, _smtpPassword);
                client.EnableSsl = true;
                client.DeliveryMethod = SmtpDeliveryMethod.Network;

                var message = new MailMessage
                {
                    From = new MailAddress(_fromEmail, _fromName),
                    Subject = verificationType == "signup" ? "Verify Your MovRec Account" : "MovRec Password Reset",
                    IsBodyHtml = true
                };

                // Add proper headers
                message.Headers.Add("X-Mailer", "MovRec");
                message.Headers.Add("X-Priority", "1");
                message.Headers.Add("X-MSMail-Priority", "High");
                message.Headers.Add("Importance", "High");

                // Create HTML and plain text versions
                string htmlBody = GetHtmlEmailBody(verificationCode, verificationType);
                string plainTextBody = GetPlainTextEmailBody(verificationCode, verificationType);

                // Create alternative views
                var htmlView = AlternateView.CreateAlternateViewFromString(htmlBody, null, MediaTypeNames.Text.Html);
                var plainTextView = AlternateView.CreateAlternateViewFromString(plainTextBody, null, MediaTypeNames.Text.Plain);

                message.AlternateViews.Add(plainTextView);
                message.AlternateViews.Add(htmlView);

                message.To.Add(email);

                await client.SendMailAsync(message);
            }
        }

        private string GetHtmlEmailBody(string code, string verificationType)
        {
            return $@"
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset='utf-8'>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .code {{ font-size: 24px; font-weight: bold; color: #ff6347; padding: 10px; background: #f5f5f5; text-align: center; }}
                        .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class='container'>
                        <h2>{(verificationType == "signup" ? "Welcome to MovRec!" : "Password Reset Request")}</h2>
                        <p>{(verificationType == "signup"
                            ? "Thank you for signing up! Please use the following code to verify your email address:"
                            : "You have requested to reset your password. Please use the following code to proceed:")}</p>
                        <div class='code'>{code}</div>
                        <p>This code will expire in 24 hours.</p>
                        <div class='footer'>
                            <p>If you didn't request this, please ignore this email.</p>
                            <p>Best regards,<br>The MovRec Team</p>
                        </div>
                    </div>
                </body>
                </html>";
        }

        private string GetPlainTextEmailBody(string code, string verificationType)
        {
            return $@"
                {(verificationType == "signup" ? "Welcome to MovRec!" : "Password Reset Request")}

                {(verificationType == "signup"
                    ? "Thank you for signing up! Please use the following code to verify your email address:"
                    : "You have requested to reset your password. Please use the following code to proceed:")}

                Verification Code: {code}

                This code will expire in 24 hours.

                If you didn't request this, please ignore this email.

                Best regards,
                The MovRec Team";
        }

        public async Task SendPasswordResetEmailAsync(string email, string resetCode)
        {
            await SendVerificationEmailAsync(email, resetCode, "password_reset");
        }
    }
}