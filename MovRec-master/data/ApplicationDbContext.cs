using Microsoft.EntityFrameworkCore;
using MovRec.Models;

namespace MovRec.data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options) { }

    public DbSet<Movie> Movies { get; set; }
    public DbSet<User> Users { get; set; }
    public DbSet<Genres> Genres { get; set; }

    public DbSet<WatchEvent> WatchEvents { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<WatchEvent>()
            .HasKey(w => new { w.movie_id, w.user_id });

        modelBuilder.Entity<Genres>()
            .HasKey(g => new { g.movie_id, g.genre });
    }

}

