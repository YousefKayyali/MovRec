import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

# Set data path to your data location
data_path = r"C:\Users\user\Desktop\movrec_data\update_3"

# Load CSV files
genres_df = pd.read_csv(os.path.join(data_path, "genres.csv"))
movies_df = pd.read_csv(os.path.join(data_path, "movie_2.csv"))
ratings_df = pd.read_csv(os.path.join(data_path, "rating_2.csv"))

# --- Preprocessing ---
# Rename and standardize movie ID column
movies_df.rename(columns={"Movie ID": "movieId"}, inplace=True)
movies_df['movieId'] = movies_df['movieId'].astype(str)
genres_df['movie_id'] = genres_df['movie_id'].astype(str)
ratings_df['movieId'] = ratings_df['movieId'].astype(str)

# Aggregate genres into a set for each movie
genres_agg = genres_df.groupby('movie_id')['genre'].apply(set).to_dict()
movies_df['genres'] = movies_df['movieId'].apply(lambda x: genres_agg.get(x, set()))

# Process Cast: convert comma-separated string into a set
movies_df['cast_set'] = movies_df['Cast'].fillna("").apply(
    lambda x: set(n.strip() for n in x.split(',')) if x != "" else set()
)

# Process Director: strip whitespace and fill missing values
movies_df['director'] = movies_df['Director'].fillna("").apply(lambda x: x.strip())

# Process Production Companies: convert comma-separated string into a set
movies_df['prod_companies'] = movies_df['Production Companies'].fillna("").apply(
    lambda x: set(n.strip() for n in x.split(',')) if x != "" else set()
)

# Fill missing Overview with an empty string
movies_df['Overview'] = movies_df['Overview'].fillna("")

# --- Collaborative Filtering Setup ---
# Create pivot table for ratings and compute cosine similarity
rating_matrix = ratings_df.pivot_table(index='movieId', columns='userId', values='rating').fillna(0)
cf_similarity = cosine_similarity(rating_matrix)
movie_ids_cf = rating_matrix.index.tolist()
cf_similarity_df = pd.DataFrame(cf_similarity, index=movie_ids_cf, columns=movie_ids_cf)

# --- Precompute TF-IDF and Overview Similarity ---
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['Overview'])
overview_sim_matrix = cosine_similarity(tfidf_matrix)

# Mapping from movieId to index in movies_df for TF-IDF lookup
movieId_to_index = {row['movieId']: idx for idx, row in movies_df.iterrows()}

# --- Define Jaccard Similarity Function for Set-Based Features ---
def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# --- Build Recommendations with a 30% CF / 70% Content Hybrid ---
results = []  # To store recommendation pairs

for idx, movie in tqdm(movies_df.iterrows(), total=movies_df.shape[0], desc="Processing movies"):
    current_movie_id = movie['movieId']
    idx1 = movieId_to_index[current_movie_id]
    sim_scores = {}
    
    # Compare current movie with every other movie
    for _, candidate in movies_df[movies_df['movieId'] != current_movie_id].iterrows():
        candidate_movie_id = candidate['movieId']
        idx2 = movieId_to_index[candidate_movie_id]
        
        # --- Collaborative Filtering (CF) Component ---
        if current_movie_id in rating_matrix.index and candidate_movie_id in rating_matrix.index:
            cf_sim = cf_similarity_df.loc[current_movie_id, candidate_movie_id]
        else:
            cf_sim = None  # CF score not available
        
        # --- Content-Based Component ---
        # Overview (story theme) similarity from TF-IDF cosine similarity
        overview_sim_val = overview_sim_matrix[idx1, idx2]
        
        # Director similarity: 1 if directors match and are non-empty; else 0.
        director_sim = 1 if movie['director'] and candidate['director'] and movie['director'] == candidate['director'] else 0
        
        # Cast similarity using Jaccard similarity
        cast_sim = jaccard_similarity(movie['cast_set'], candidate['cast_set'])
        
        # Genres similarity using Jaccard similarity
        genre_sim = jaccard_similarity(movie['genres'], candidate['genres'])
        
        # Production Companies similarity using Jaccard similarity
        prod_comp_sim = jaccard_similarity(movie['prod_companies'], candidate['prod_companies'])
        
        # Compute raw content score with specified weights:
        # 30% overview, 15% director, 15% cast, 10% genres, 10% production companies
        content_raw = (0.30 * overview_sim_val + 
                       0.15 * director_sim + 
                       0.15 * cast_sim + 
                       0.15 * genre_sim + 
                       0.10 * prod_comp_sim)
        # Normalize content score (max possible raw score is 0.85)
        content_sim = content_raw / 0.85
        
        # --- Combine the Two Scores ---
        # Use CF component if available; otherwise, fallback to content similarity.
        if cf_sim is not None:
            combined_score = 0.15 * cf_sim + 0.85 * content_sim
        else:
            combined_score = content_sim
        
        sim_scores[candidate_movie_id] = combined_score
    
    # For the current movie, select the top 30 similar movies.
    top_similar = sorted(sim_scores.items(), key=lambda x: x[1], reverse=True)[:30]
    for sim_movie_id, score in top_similar:
        results.append({
            'movie_id': current_movie_id,
            'similar_movie_id': sim_movie_id,
            'score': score
        })

# Write recommendations to CSV.
results_df = pd.DataFrame(results)
output_file = os.path.join(data_path, "movie_similarities_15_85_new.csv")
results_df.to_csv(output_file, index=False)

print(f"Recommendation CSV created at: {output_file}")
