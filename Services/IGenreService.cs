using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MovRec.Controllers;
using MovRec.Models;

namespace MovRec.Services
{
    public interface IGenreService
    {List<Genre> GetAvailableGenres();
    Task<bool> SaveUserGenres(int userId, List<string> selectedGenres);
    Task<List<string>> GetUserGenres(int userId);
    }
}