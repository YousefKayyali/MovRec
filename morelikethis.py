import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm  # for progress bar

# Set data path to the desired output location
data_path = r"C:\Users\user\Desktop\movrec_data\update_3"

# Load CSV files
genres_df = pd.read_csv(os.path.join(data_path, "genres.csv"))
movies_df = pd.read_csv(os.path.join(data_path, "movie_2.csv"))
ratings_df = pd.read_csv(os.path.join(data_path, "rating_2.csv"))

# --- Preprocessing ---
movies_df.rename(columns={"Movie ID": "movieId"}, inplace=True)
movies_df['movieId'] = movies_df['movieId'].astype(str)
genres_df['movie_id'] = genres_df['movie_id'].astype(str)
ratings_df['movieId'] = ratings_df['movieId'].astype(str)

# Aggregate genres into a set for each movie
genres_agg = genres_df.groupby('movie_id')['genre'].apply(set).to_dict()
movies_df['genres'] = movies_df['movieId'].apply(lambda x: genres_agg.get(x, set()))

# Process cast: assume names are comma separated.
movies_df['cast_set'] = movies_df['Cast'].fillna("").apply(lambda x: set(n.strip() for n in x.split(',')) if x != "" else set())

# Process director: fill missing values and strip whitespace.
movies_df['director'] = movies_df['Director'].fillna("").apply(lambda x: x.strip())

# Fill missing overview with an empty string.
movies_df['Overview'] = movies_df['Overview'].fillna("")

# --- Determine Which Movies Have Enough Ratings ---
ratings_count = ratings_df.groupby('movieId').size()
threshold = 50  # threshold for using collaborative filtering
movies_with_enough_ratings = set(ratings_count[ratings_count >= threshold].index)

# --- Collaborative Filtering Setup ---
rating_matrix = ratings_df.pivot_table(index='movieId', columns='userId', values='rating').fillna(0)
cf_similarity = cosine_similarity(rating_matrix)
movie_ids_cf = rating_matrix.index.tolist()
cf_similarity_df = pd.DataFrame(cf_similarity, index=movie_ids_cf, columns=movie_ids_cf)

# --- Precompute TF-IDF and Overview Similarity ---
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['Overview'])
overview_sim_matrix = cosine_similarity(tfidf_matrix)

# Create mapping from movieId to index in movies_df
movieId_to_index = {row['movieId']: idx for idx, row in movies_df.iterrows()}

# --- Similarity Functions ---
def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def content_similarity(movie1, movie2, overview_sim):
    # Genre similarity (Jaccard)
    genre_sim = jaccard_similarity(movie1['genres'], movie2['genres'])
    # Cast similarity (Jaccard)
    cast_sim = jaccard_similarity(movie1['cast_set'], movie2['cast_set'])
    # Director similarity (1 if same and not empty)
    director_sim = 1 if (movie1['director'] and movie1['director'] == movie2['director']) else 0
    # Overview similarity is provided from the precomputed matrix
    overview_sim_val = overview_sim
    # Combined weighted score (adjust weights as needed)
    score = 0.3 * genre_sim + 0.3 * cast_sim + 0.2 * director_sim + 0.2 * overview_sim_val
    return score

# --- Build Recommendations ---
results = []  # store recommendation pairs

# Using tqdm to track progress through movies
for idx, movie in tqdm(movies_df.iterrows(), total=movies_df.shape[0], desc="Processing movies"):
    current_movie_id = movie['movieId']
    sim_scores = {}
    
    if current_movie_id in movies_with_enough_ratings and current_movie_id in cf_similarity_df.index:
        # Use collaborative filtering
        sims = cf_similarity_df.loc[current_movie_id].drop(current_movie_id)
        top_similar = sims.sort_values(ascending=False).head(10)
        for sim_movie_id, score in top_similar.items():
            sim_scores[sim_movie_id] = score
    else:
        # Use content-based filtering
        # Restrict candidate pool: only movies sharing at least one genre (if available)
        if movie['genres']:
            candidate_df = movies_df[movies_df['movieId'] != current_movie_id].copy()
            candidate_df = candidate_df[candidate_df['genres'].apply(lambda x: len(movie['genres'].intersection(x)) > 0)]
        else:
            candidate_df = movies_df[movies_df['movieId'] != current_movie_id]
        
        # Get index for current movie in the TF-IDF matrix
        idx1 = movieId_to_index[current_movie_id]
        
        # Compute similarities for each candidate in the reduced pool.
        for _, candidate in candidate_df.iterrows():
            candidate_movie_id = candidate['movieId']
            idx2 = movieId_to_index[candidate_movie_id]
            overview_sim_val = overview_sim_matrix[idx1, idx2]
            score = content_similarity(movie, candidate, overview_sim_val)
            sim_scores[candidate_movie_id] = score
        
        # Get top 10 candidates by content similarity score.
        sim_scores = dict(sorted(sim_scores.items(), key=lambda x: x[1], reverse=True)[:10])
    
    # Save each recommendation pair into results.
    for sim_movie_id in sim_scores.keys():
        results.append({'movie_id': current_movie_id, 'similar_movie_id': sim_movie_id})

# Write results to CSV in the specified directory.
results_df = pd.DataFrame(results)
output_file = os.path.join(data_path, "movie_similarities.csv")
results_df.to_csv(output_file, index=False)

print(f"Recommendation CSV created at: {output_file}")
