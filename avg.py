import pandas as pd

# Load ratings data
ratings_path = r"C:\Users\user\Desktop\movrec_data\update_3\rating_2.csv"
output_path = r"C:\Users\user\Desktop\movrec_data\update_3\avgrating.csv"

# Read the CSV file
ratings_df = pd.read_csv(ratings_path)

# Calculate the average rating per movie and count of ratings
movie_stats = ratings_df.groupby("movieId")["rating"].agg(["mean", "count"]).reset_index()

# Compute the global mean rating
C = ratings_df["rating"].mean()

# Define the minimum number of ratings required (e.g., 100)
m = 100  # You can adjust this value based on your dataset

# Compute the weighted rating using the IMDB formula
movie_stats["weighted_rating"] = (
    (movie_stats["count"] / (movie_stats["count"] + m)) * movie_stats["mean"]
) + (
    (m / (movie_stats["count"] + m)) * C
)

# Normalize to a scale of 10 and round to 2 decimal places
movie_stats["rating"] = (movie_stats["weighted_rating"] * 2).round(2)

# Keep only necessary columns
final_avg_ratings = movie_stats[["movieId", "rating"]]

# Save to CSV
final_avg_ratings.to_csv(output_path, index=False)

print("Updated avgrating.csv successfully using the IMDB formula!")