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
    public DbSet<ReferencedIn> ReferencedIn { get; set; }
    public DbSet<SimilarMovie> SimilarMovies { get; set; }
    public DbSet<EmailVerification> EmailVerifications { get; set; }
    public DbSet<UserRecommendation> UserRecommendations { get; set; }
    public DbSet<ModelRecommendations> ModelRecommendations { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<WatchEvent>()
            .HasKey(w => new { w.movie_id, w.user_id });

        modelBuilder.Entity<Genres>()
            .HasKey(g => new { g.movie_id, g.genre });

        modelBuilder.Entity<ReferencedIn>()
            .HasKey(r => new { r.movie_id, r.user_id });

        modelBuilder.Entity<ReferencedIn>()
            .HasOne(r => r.Movie)
            .WithMany()
            .HasForeignKey(r => r.movie_id);

        modelBuilder.Entity<ReferencedIn>()
            .HasOne(r => r.User)
            .WithMany()
            .HasForeignKey(r => r.user_id);

        modelBuilder.Entity<SimilarMovie>()
            .HasKey(s => new { s.movie_id, s.similer_movie_id });

        modelBuilder.Entity<SimilarMovie>()
            .HasOne(s => s.Movie)
            .WithMany()
            .HasForeignKey(s => s.movie_id);

        modelBuilder.Entity<SimilarMovie>()
            .HasOne(s => s.SimilarMovieNavigation)
            .WithMany()
            .HasForeignKey(s => s.similer_movie_id);

        modelBuilder.Entity<UserRecommendation>()
            .HasKey(ur => new { ur.user_id, ur.movie_id });

        modelBuilder.Entity<UserRecommendation>()
            .HasOne(ur => ur.Movie)
            .WithMany()
            .HasForeignKey(ur => ur.movie_id);

        modelBuilder.Entity<UserRecommendation>()
            .HasOne(ur => ur.User)
            .WithMany()
            .HasForeignKey(ur => ur.user_id);

        modelBuilder.Entity<ModelRecommendations>()
            .HasKey(mr => new { mr.user_id, mr.movie_id });

        modelBuilder.Entity<ModelRecommendations>()
            .HasOne(mr => mr.Movie)
            .WithMany()
            .HasForeignKey(mr => mr.movie_id);

        modelBuilder.Entity<ModelRecommendations>()
            .HasOne(mr => mr.User)
            .WithMany()
            .HasForeignKey(mr => mr.user_id);
    }
}

