import pandas as pd
import os
lpath=r'cpdata3v2'
rating=pd.read_csv(lpath+'\\ratings.csv')
movies=pd.read_csv(lpath+'\\movies.csv')
links=pd.read_csv(lpath+'\\links.csv')
temp_above_600=rating.groupby('userId').filter(lambda x:len(x)>=600)
print(temp_above_600.shape)
movie_counts = rating['movieId'].value_counts().to_dict()
user_counts  = rating['userId' ].value_counts().to_dict()
ulp = []
for w, (idx, row) in enumerate(temp_above_600.iterrows(), 1):
    user_id  = row['userId']
    movie_id = row['movieId']
    if movie_counts.get(movie_id, 0) > 50 and user_counts.get(user_id, 0) > 600:
        movie_counts[movie_id] -= 1
        user_counts[user_id]  -= 1
        ulp.append((user_id, movie_id))
    if w % 500_000 == 0:
        print(w)
to_remove=pd.MultiIndex.from_tuples(ulp,names=['userId', 'movieId'])
keep_mask = ~rating.set_index(['userId', 'movieId']).index.isin(to_remove)
print(len(ulp))
print(len(rating[keep_mask].movieId.unique()))
rating=rating[keep_mask]
print(rating.shape)
movies.drop(labels=['Average Rating', 'Vote Count','Poster Path', 'Backdrop Path', 'Keywords', 'Similar Movies'],axis=1,inplace=True)
lpath=r'cpdata4v2'
os.makedirs(lpath,exist_ok=True)
links.to_csv(lpath+'\\links.csv',index=False)
rating.to_csv(lpath+'\\ratings.csv',index=False)
movies.to_csv(lpath+'\\movies.csv',index=False)