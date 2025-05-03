using Microsoft.AspNetCore.Mvc;
using MovRec.Models;
using MovRec.Models.ViewModels;
using MovRec.data;

namespace MovRec.Controllers
{
    public class CategoriesController : Controller
    {
        private readonly ApplicationDbContext _context;

        public CategoriesController(ApplicationDbContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            var model = new CategoriesViewModel();
            return View(model);
        }

        [HttpPost]
        public async Task<IActionResult> SaveCategories(CategoriesViewModel model)
        {
            if (model.SelectedCategories == null || !model.SelectedCategories.Any())
            {
                ModelState.AddModelError(string.Empty, "Please select at least one category.");
                return View("Index", model);
            }
            if (ModelState.IsValid)
            {
                var userId = HttpContext.Session.GetInt32("UserId");
                if (userId == null)
                {
                    return RedirectToAction("Login", "Account");
                }

                var user = await _context.Users.FindAsync(userId);
                if (user != null)
                {
                    // Join the selected categories with commas
                    user.gener = string.Join(",", model.SelectedCategories);
                    await _context.SaveChangesAsync();

                    // Set session variables and redirect to UserHome
                    HttpContext.Session.SetInt32("UserId", user.user_id);
                    HttpContext.Session.SetString("Username", user.username);
                    return RedirectToAction("UserHome", "Home");
                }
            }

            // If validation fails, return to the categories page
            return View("Index", model);
        }
    }
}