using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Http;

namespace MovRec.Filters;

public class AuthorizeUserAttribute : Attribute, IAuthorizationFilter
{
    public void OnAuthorization(AuthorizationFilterContext context)
    {
        // Check if session is available
        if (!IsSessionAvailable(context.HttpContext))
        {
            context.Result = new RedirectToActionResult("Login", "Account", new 
            { 
                returnUrl = context.HttpContext.Request.Path 
            });
            return;
        }

        // Check if user is logged in
        if (!IsUserLoggedIn(context.HttpContext))
        {
            context.Result = new RedirectToActionResult("Login", "Account", new 
            { 
                returnUrl = context.HttpContext.Request.Path 
            });
        }
    }

    private bool IsSessionAvailable(HttpContext httpContext)
    {
        try
        {
            // This will throw if session isn't configured
            return httpContext.Session.IsAvailable;
        }
        catch
        {
            return false;
        }
    }

    private bool IsUserLoggedIn(HttpContext httpContext)
    {
        return httpContext.Session.GetInt32("UserId") != null;
    }
}