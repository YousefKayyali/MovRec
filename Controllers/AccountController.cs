using BCrypt.Net;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MovRec.data;
using MovRec.Models;
using MovRec.Filters;


public class AccountController : Controller
{
    private readonly ApplicationDbContext _context;

    public AccountController(ApplicationDbContext context)
    {
        _context = context;
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
    public IActionResult VerifyEmail(string email)
    {
        if (_context.Users.Any(u => u.email.ToLower() == email.ToLower()))
        {
            return Json($"Email '{email}' is already registered.");
        }
        return Json(true);
    }

    [HttpPost]
    public async Task<IActionResult> SignUp(User user)
    {
        // Check if username exists
        if (_context.Users.Any(u => u.username.ToLower() == user.username.ToLower()))
        {
            ModelState.AddModelError("username", "Username is already taken");
        }

        // Check if email exists
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
                _context.Users.Add(user);
                await _context.SaveChangesAsync();

                return RedirectToAction("Index", "Categories");
            }
            catch (Exception ex)
            {
                ModelState.AddModelError(string.Empty, "An error occurred while saving the data.");
                return View(user);
            }
        }

        return View(user);
    }


    // POST: /Account/Login
    [HttpPost]
    [AllowAnonymous]
    public async Task<IActionResult> Login(LoginViewModel model, string returnUrl = null)
    {
        ViewData["ReturnUrl"] = returnUrl;
        if (ModelState.IsValid)
        {
            // Find the user by email or username
            var user = await _context.Users.FirstOrDefaultAsync(u => u.email == model.email);

            if (user != null)
            {
                // Verify the password
                bool isPasswordValid = BCrypt.Net.BCrypt.Verify(model.password, user.password);

                if (isPasswordValid)
                {
                    HttpContext.Session.SetInt32("UserId", user.user_id);
                    HttpContext.Session.SetString("Username", user.username);

                    return RedirectToLocal(returnUrl);
                }
            }
            // If the user is not found or the password is invalid, show an error
            ModelState.AddModelError("", "Invalid email or password.");

        }

        // If the model state is not valid, return the view with the model to show validation errors
        return View(model);
    }

    public IActionResult ForgotPassword()
    {
        return View();
    }

    [HttpPost]
    public IActionResult ForgotPassword(string email)
    {
        // Add your logic to send a password reset code to the email
        // For now, we'll just return a success message
        ViewBag.Message = $"Code sent to {email}";
        return View();
    }


    // POST: /Account/UpdateProfile
    [HttpPost]
    [AuthorizeUser]
    [ValidateAntiForgeryToken]
    public IActionResult UpdateProfile(User model)
    {
        if (ModelState.IsValid)
        {
            var user = _context.Users.Find(model.user_id);
            if (user != null)
            {
                user.email = model.email;
                user.username = model.username;
                user.birth_date = model.birth_date;

                _context.SaveChanges();
                HttpContext.Session.SetString("Username", user.username);

                ViewData["SuccessMessage"] = "Profile updated successfully";
                return View("UserProfile", user);
            }
        }
        return View("UserProfile", model);
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
        return RedirectToAction("UserProfile");
    }
}