Movie Recommendation System 
1 · Purpose
The project delivers movie recommendations by combining
• data-cleaning pipelines,
• a custom tokenizer,
• deep-learning models in PyTorch, and
• database-driven inference / updates in PostgreSQL.

All heavy work (feature storage, user vectors, recommendation lists) is executed inside the database to keep the API layer light.

2 · Data-Preparation Scripts
work1.py → work4.py
These four scripts form a staged ETL pipeline that starts with raw MovieLens and TMDB files and finishes with compact, ID-re-mapped CSVs ready for modeling.

Stage 1 (work1.py) removes duplicates and nulls from links.csv, then saves the cleaned file to cpdata1v2/.

Stage 2 (work2.py) cross-filters links, ratings, and enriched movies_data.csv so that every referenced ID exists in all three sets, then writes them to cpdata2v2/.

Stage 3 (work3.py) prunes rare items and very small user profiles, remaps TMDB and MovieLens IDs to compact 1…N indices, factorizes user IDs, strips timestamp, and outputs cpdata3v2/.

Stage 4 (work4.py) removes extreme “super-rater” noise (> 600 ratings) and drops unused movie columns, producing the final training bundle in cpdata4v2/.

These steps ensure the rating matrix is dense enough for Pearson correlation while staying small enough for GPU memory.

3 · Custom Tokenization
tokinzation.py builds an in-house tokenizer—no external NLP libraries.
It lowercases, strips punctuation, splits by comma or whitespace, assigns integer IDs, pads/truncates to fixed sequence lengths, and serializes the tensors (title.pt, cast.pt, etc.) for later embedding layers.

4 · Neural Models
4.1 · Base Matrix-Factorization Model
calculate_user_defualts_lattent_attribute.py loads a pretrained checkpoint (base_model_MAE_0.6602.pth) and extracts the 100-dimensional user embedding matrix. The mean vector becomes the “default latent attribute” for new accounts and is inserted into PostgreSQL via a trigger. 


4.2 · Online Rating Update
after_rating.py is executed whenever a user submits a new explicit rating.
Steps:

Pull the current 100-dim user vector from model.user_latent_attributes.

Run the lightweight movie-only sub-network to obtain that movie’s embedding.

Perform one step of gradient descent on the user vector only, leaving movie parameters fixed.

Write the updated vector back to user_latent_attributes and archive the old one in user_latent_attributes_backups. 


4.3 · Hybrid Deep Model for Inference
model.py defines FinalModel, which multiplies the live user vector with a rich movie representation (embeddings for title, overview, cast, genres, production companies/countries plus numeric features).
For each unseen movie, it predicts an expected rating; candidates ≥ 3 ★ are ranked and stored in model.model_recommendation. 


Alternate architectures (FunctionalModel, full MLP) appear in model2.py; keep these as experimental baselines. 


5 · User-to-User Collaborative Filtering
user_to_user_lr.py operates entirely inside the database:

Fetch the target user’s watch history.

Scan a local copy of the ratings CSV to build per-user dictionaries.

Compute Pearson correlation (not k-NN) with each other user; accept neighbours with correlation ≥ 0.65 and at least 14 shared movies.

For the top neighbours, translate their highly-rated unseen movies into predicted scores and write them to model.user_recommendation. 


This script is launched asynchronously (e.g., by cron or a message queue) so recommendations stay fresh without blocking the web API.

6 · Database Layout (essential tables only)
movies – master list, keyed by movie_id.

watch_events – every explicit user rating (user_id, movie_id, rating).

model.user_latent_attributes – 100-float vector per user.

model.user_latent_attributes_backups – one historical row per update.

model.model_recommendation – deep-model top picks, ≤ 150 rows per user.

model.user_recommendation – Pearson CF results, ≤ 150 rows per user.

model.ratings_summary1 / model.rating1 – cached averages to speed Pearson math.

7 · Operational Flow
Nightly ETL: run work1.py → work4.py, then tokinzation.py.

Model training (offline, not in repo): produce checkpoints referenced by the scripts.

Default vectors: execute calculate_user_defualts_lattent_attribute.py; database trigger inserts mean vector.

Real-time:
• User opens the app → API requests /api/recommend/{id} → backend calls model.py for neural recs, falls back to user_to_user_lr.py if cold.
• User rates a film → trigger launches after_rating.py to adapt their embedding.

8 · How to Re-run Everything Locally
Environment
• Python 3.10 + PyTorch with GPU support
• PostgreSQL ≥ 14 (create DB movrec)
• . NET 8 SDK for the API (not included in these uploads)
