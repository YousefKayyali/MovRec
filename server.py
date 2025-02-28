from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Paths to data
DATA_DIR = r"C:\Users\user\Desktop\movrec_data\update_3"
IMAGE_DIR = r"C:\Users\user\Desktop\movrec_data\images"

# Load CSV files
movies_path = os.path.join(DATA_DIR, "movie_2.csv")
ratings_path = os.path.join(DATA_DIR, "avgrating.csv")
genres_path = os.path.join(DATA_DIR, "genres.csv")

# Check if files exist
if not os.path.exists(movies_path):
    print(f"Error: File not found - {movies_path}")
if not os.path.exists(ratings_path):
    print(f"Error: File not found - {ratings_path}")
if not os.path.exists(genres_path):
    print(f"Error: File not found - {genres_path}")

# Load data into DataFrames
movies_df = pd.read_csv(movies_path) if os.path.exists(movies_path) else pd.DataFrame()
ratings_df = pd.read_csv(ratings_path) if os.path.exists(ratings_path) else pd.DataFrame()
genres_df = pd.read_csv(genres_path) if os.path.exists(genres_path) else pd.DataFrame()

# Ensure column names are correct
print("Movies DataFrame Columns:", movies_df.columns)
print("Ratings DataFrame Columns:", ratings_df.columns)
print("Genres DataFrame Columns:", genres_df.columns)

# Convert movie ID to string in all DataFrames
if "Movie ID" not in movies_df.columns:
    print("Error: 'Movie ID' column missing from movie_2.csv")
    movies_df = pd.DataFrame()
else:
    movies_df["Movie ID"] = movies_df["Movie ID"].astype(str)

if "movieId" not in ratings_df.columns:
    print("Error: 'movieId' column missing from avgrating.csv")
    ratings_df = pd.DataFrame()
else:
    ratings_df["movieId"] = ratings_df["movieId"].astype(str)

if "movie_id" not in genres_df.columns:
    print("Error: 'movie_id' column missing from genres.csv")
    genres_df = pd.DataFrame()
else:
    genres_df["movie_id"] = genres_df["movie_id"].astype(str)

# Merge movies with ratings and genres
if not movies_df.empty and not ratings_df.empty:
    movies_df = movies_df.merge(ratings_df, left_on="Movie ID", right_on="movieId", how="left")
    movies_df.drop(columns=["movieId"], inplace=True)
else:
    print("Error: Unable to merge movies with ratings. One or both DataFrames are empty.")

if not movies_df.empty and not genres_df.empty:
    movies_df = movies_df.merge(genres_df, left_on="Movie ID", right_on="movie_id", how="left")
    movies_df.drop(columns=["movie_id"], inplace=True)
else:
    print("Error: Unable to merge movies with genres. One or both DataFrames are empty.")

# Replace NaN values with None
movies_df = movies_df.where(pd.notnull(movies_df), None)

# Preprocess genres into a dictionary for faster lookups
genres_dict = {}
if not genres_df.empty and "movie_id" in genres_df.columns and "genre" in genres_df.columns:
    genres_dict = genres_df.groupby("movie_id")["genre"].apply(list).to_dict()
else:
    print("Error: Unable to create genres dictionary. Genres DataFrame is empty or missing required columns.")
    genres_dict = {}

@app.route("/")
def home():
    return "Movie Recommendation Server is Running!"

@app.route("/movies", methods=["GET"])
def get_movies():
    if movies_df.empty:
        return jsonify({"error": "No movies found"}), 404

    # Get pagination, sorting, and genre parameters
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    sort_by = request.args.get("sort_by", "rating")
    genres = request.args.getlist("genre")  # Get list of genres

    # Filter movies by genres if provided
    if genres:
        # Get movie IDs that belong to all selected genres
        genre_movie_ids = set(genres_df[genres_df["genre"].isin(genres)]["movie_id"].tolist())
        for genre in genres:
            genre_movie_ids.intersection_update(set(genres_df[genres_df["genre"] == genre]["movie_id"].tolist()))
        filtered_movies = movies_df[movies_df["Movie ID"].isin(genre_movie_ids)]
    else:
        filtered_movies = movies_df

    # Sort movies by rating (descending)
    sorted_movies = filtered_movies.sort_values(by=sort_by, ascending=False)

    # Paginate movies
    total_movies = len(sorted_movies)
    start = (page - 1) * per_page
    end = start + per_page

    if end > total_movies:
        end = total_movies

    paginated_movies = sorted_movies.iloc[start:end]

    return jsonify({
        "movies": paginated_movies.to_dict(orient="records"),
        "total": total_movies,
        "page": page,
        "per_page": per_page
    })

@app.route("/genres", methods=["GET"])
def get_genres():
    if genres_df.empty:
        return jsonify({"error": "No genres found"}), 404

    unique_genres = genres_df["genre"].unique().tolist()
    return jsonify(unique_genres)

@app.route("/movie/<movie_id>", methods=["GET"])
def get_movie_details(movie_id):
    if "Movie ID" not in movies_df.columns:
        return jsonify({"error": "Movie data not available"}), 500

    movie = movies_df[movies_df["Movie ID"] == movie_id]
    if movie.empty:
        return jsonify({"error": "Movie not found"}), 404

    movie_data = movie.iloc[0].to_dict()
    movie_data["genres"] = genres_dict.get(movie_id, [])

    if "rating" in movie_data and movie_data["rating"] is not None:
        movie_data["rating"] = round(float(movie_data["rating"]), 1)
    else:
        movie_data["rating"] = "N/A"

    print("Movie Data:", movie_data)
    return jsonify(movie_data)

@app.route("/search", methods=["GET"])
def search_movies():
    query = request.args.get("query", "").strip().lower()
    if not query:
        return jsonify([])

    results = movies_df[movies_df["Title"].str.lower().str.contains(query)]
    results = results.head(10)
    return jsonify(results.to_dict(orient="records"))

@app.route("/images/<folder>/<filename>")
def get_image(folder, filename):
    if folder not in ["posters", "backdrops"]:
        return jsonify({"error": "Invalid folder"}), 400

    if folder == "posters":
        full_filename = f"{filename}poster.jpg"
    elif folder == "backdrops":
        full_filename = f"{filename}backdrop.jpg"

    print(f"Requested image path: {os.path.join(IMAGE_DIR, folder, full_filename)}")
    image_path = os.path.join(IMAGE_DIR, folder, full_filename)
    
    if not os.path.exists(image_path):
        placeholder_path = os.path.join(IMAGE_DIR, folder, "placeholder.jpg")
        if os.path.exists(placeholder_path):
            return send_from_directory(os.path.join(IMAGE_DIR, folder), "placeholder.jpg")
        else:
            return jsonify({"error": "Image not found"}), 404

    return send_from_directory(os.path.join(IMAGE_DIR, folder), full_filename)

if __name__ == "__main__":
    app.run(debug=False, port=8000)