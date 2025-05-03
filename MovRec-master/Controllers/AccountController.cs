using BCrypt.Net;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Models;
using MovRec.Filters;
using MovRec.Services;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;

public class AccountController : Controller
{
    private readonly ApplicationDbContext _context;
    private readonly IVerificationService _verificationService;
    private readonly IEmailService _emailService;

    public AccountController(ApplicationDbContext context, IVerificationService verificationService, IEmailService emailService)
    {
        _context = context;
        _verificationService = verificationService;
        _emailService = emailService;
    }
    [AllowAnonymous]
    public ActionResult Login(string returnUrl = null)
    {
        ViewData["ReturnUrl"] = returnUrl;
        return View();
    }
    [AuthorizeUser]
    public IActionResult UserProfile()
    {
        var userId = HttpContext.Session.GetInt32("UserId");
        var user = _context.Users.Find(userId);
        return View(user);
    }



    public IActionResult SignUp()
    {
        return View();
    }
    [HttpGet]
    public async Task<IActionResult> VerifyUsername(string username)
    {
        if (string.IsNullOrWhiteSpace(username))
        {
            return Json("Username is required.");
        }

        bool exists = await _context.Users
            .AnyAsync(u => u.username.ToLower() == username.ToLower());

        return exists ? Json($"Username '{username}' is already taken.") : Json(true);
    }
    [HttpGet]
    public IActionResult VerifyEmail(string type)
    {
        var userId = HttpContext.Session.GetInt32("PendingVerificationUserId");
        if (userId == null)
        {
            return RedirectToAction("Login");
        }

        ViewBag.VerificationType = type;
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> SignUp(User user)
    {
        if (_context.Users.Any(u => u.username.ToLower() == user.username.ToLower()))
        {
            ModelState.AddModelError("username", "Username is already taken");
        }

        if (_context.Users.Any(u => u.email.ToLower() == user.email.ToLower()))
        {
            ModelState.AddModelError("email", "Email is already registered");
        }

        if (ModelState.IsValid)
        {
            try
            {
                user.password = BCrypt.Net.BCrypt.HashPassword(user.password);
                user.create_date = DateTime.UtcNow;
                user.is_active = false; // User is not active until email is verified
                _context.Users.Add(user);
                await _context.SaveChangesAsync();

                // Generate and send verification code
                await _verificationService.GenerateVerificationCodeAsync(user.user_id, "signup");

                // Store user ID in session for verification
                HttpContext.Session.SetInt32("PendingVerificationUserId", user.user_id);

                return RedirectToAction("VerifyEmail", new { type = "signup" });
            }
            catch (Exception ex)
            {
                ModelState.AddModelError(string.Empty, "An error occurred while saving the data.");
                return View(user);
            }
        }

        return View(user);
    }

    [HttpPost]
    public async Task<IActionResult> VerifyEmail(string code, string type)
    {
        var userId = HttpContext.Session.GetInt32("PendingVerificationUserId");
        if (userId == null)
        {
            return RedirectToAction("Login");
        }

        if (await _verificationService.VerifyCodeAsync(userId.Value, code, type))
        {
            if (type == "signup")
            {
                var user = await _context.Users.FindAsync(userId);
                if (user != null)
                {
                    user.is_active = true;
                    await _context.SaveChangesAsync();

                    HttpContext.Session.SetInt32("UserId", user.user_id);
                    HttpContext.Session.SetString("Username", user.username);
                    HttpContext.Session.Remove("PendingVerificationUserId");

                    return RedirectToAction("Index", "Categories");
                }
            }
            else if (type == "password_reset")
            {
                HttpContext.Session.SetInt32("ResetPasswordUserId", userId.Value);
                return RedirectToAction("ResetPassword");
            }
        }

        ModelState.AddModelError("", "Invalid verification code");
        ViewBag.VerificationType = type;
        return View();
    }

    [HttpGet]
    public IActionResult ForgotPassword()
    {
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> ForgotPassword(ForgotPasswordViewModel model)
    {
        if (!ModelState.IsValid)
        {
            return View(model);
        }

        var user = await _context.Users.FirstOrDefaultAsync(u => u.email == model.Email);
        if (user == null)
        {
            ModelState.AddModelError("", "No account found with this email address.");
            return View(model);
        }

        // Generate and send verification code
        await _verificationService.GenerateVerificationCodeAsync(user.user_id, "password_reset");

        // Store user ID in session for verification
        HttpContext.Session.SetInt32("PendingVerificationUserId", user.user_id);

        return RedirectToAction("VerifyEmail", new { type = "password_reset" });
    }

    public IActionResult ResetPassword()
    {
        var userId = HttpContext.Session.GetInt32("ResetPasswordUserId");
        if (userId == null)
        {
            return RedirectToAction("Login");
        }

        return View();
    }

    [HttpPost]
    public async Task<IActionResult> ResetPassword(ResetPasswordViewModel model)
    {
        var userId = HttpContext.Session.GetInt32("ResetPasswordUserId");
        if (userId == null)
        {
            return RedirectToAction("Login");
        }

        if (ModelState.IsValid)
        {
            var user = await _context.Users.FindAsync(userId);
            if (user != null)
            {
                user.password = BCrypt.Net.BCrypt.HashPassword(model.NewPassword);
                await _context.SaveChangesAsync();

                HttpContext.Session.Remove("ResetPasswordUserId");
                return RedirectToAction("Login");
            }
        }

        return View(model);
    }

    // POST: /Account/Login
    [HttpPost]
    [AllowAnonymous]
    public async Task<IActionResult> Login(LoginViewModel model, string returnUrl = null)
    {
        ViewData["ReturnUrl"] = returnUrl;
        if (ModelState.IsValid)
        {
            // Find the user by username
            var user = await _context.Users.FirstOrDefaultAsync(u => u.username == model.username);

            if (user != null)
            {
                // Verify the password
                bool isPasswordValid = BCrypt.Net.BCrypt.Verify(model.password, user.password);

                if (isPasswordValid)
                {
                    HttpContext.Session.SetInt32("UserId", user.user_id);
                    HttpContext.Session.SetString("Username", user.username);

                    return RedirectToAction("UserHome", "Home");
                }
            }
            // If the user is not found or the password is invalid, show an error
            ModelState.AddModelError("", "Invalid username or password.");
        }

        // If the model state is not valid, return the view with the model to show validation errors
        return View(model);
    }

    // POST: /Account/UpdateProfile
    [HttpPost]
    [AuthorizeUser]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> UpdateProfile([FromForm] string email, [FromForm] string username, [FromForm] DateOnly birth_date)
    {
        var userId = HttpContext.Session.GetInt32("UserId");
        if (userId == null)
        {
            return Json(new { success = false, errors = new { general = "User not logged in" } });
        }

        var user = await _context.Users.FindAsync(userId);
        if (user == null)
        {
            return Json(new { success = false, errors = new { general = "User not found" } });
        }

        // Create a dictionary to track which fields were updated
        var updatedFields = new Dictionary<string, string>();
        if (email != null) updatedFields["email"] = email;
        if (username != null) updatedFields["username"] = username;
        if (birth_date != default) updatedFields["birth_date"] = birth_date.ToString();

        // Validate each updated field
        foreach (var field in updatedFields)
        {
            switch (field.Key)
            {
                case "username":
                    if (field.Value != user.username)
                    {
                        var usernameExists = await _context.Users
                            .AnyAsync(u => u.username.ToLower() == field.Value.ToLower() && u.user_id != userId);
                        if (usernameExists)
                        {
                            return Json(new { success = false, errors = new { username = "Username is already taken" } });
                        }
                    }
                    break;

                case "email":
                    if (field.Value != user.email)
                    {
                        var emailExists = await _context.Users
                            .AnyAsync(u => u.email.ToLower() == field.Value.ToLower() && u.user_id != userId);
                        if (emailExists)
                        {
                            return Json(new { success = false, errors = new { email = "Email is already registered" } });
                        }
                    }
                    break;
            }
        }

        try
        {
            // Update only the fields that were provided
            if (email != null) user.email = email;
            if (username != null) user.username = username;
            if (birth_date != default) user.birth_date = birth_date;

            await _context.SaveChangesAsync();

            // Update session if username was changed
            if (username != null)
            {
                HttpContext.Session.SetString("Username", user.username);
            }

            return Json(new { success = true });
        }
        catch (Exception ex)
        {
            return Json(new { success = false, errors = new { general = "An error occurred while saving your changes" } });
        }
    }
    // GET: /Account/ChangePassword

    [AuthorizeUser]
    public IActionResult ChangePassword()
    {
        return View();
    }

    [HttpPost]
    [AuthorizeUser]
    [ValidateAntiForgeryToken]
    public IActionResult ChangePassword(ChangePasswordViewModel model)
    {
        if (ModelState.IsValid)
        {
            var userId = HttpContext.Session.GetInt32("UserId");
            var user = _context.Users.Find(userId);

            if (BCrypt.Net.BCrypt.Verify(model.OldPassword, user.password))
            {
                user.password = BCrypt.Net.BCrypt.HashPassword(model.NewPassword);
                _context.SaveChanges();

                ViewData["SuccessMessage"] = "Password changed successfully";
                return RedirectToAction("UserProfile");
            }
            ModelState.AddModelError("OldPassword", "Current password is incorrect");
        }
        return View(model);
    }
    [HttpPost]
    [ValidateAntiForgeryToken]
    public IActionResult Logout()
    {
        HttpContext.Session.Clear();
        return RedirectToAction("Index", "Home");
    }

    private IActionResult RedirectToLocal(string returnUrl)
    {
        if (Url.IsLocalUrl(returnUrl))
        {
            return Redirect(returnUrl);
        }
        return RedirectToAction("UserHome", "Home");
    }
}